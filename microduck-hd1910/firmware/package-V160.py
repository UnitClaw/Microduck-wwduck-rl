#!/usr/bin/env python3
"""Produce R17 V160/control.37 from the user's V159 package and new ARM64 binaries.

Refuses to issue a release if native binaries are missing, are AArch64-incompatible,
are unchanged from V159, or do not carry control.37 identity. No Zero access.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

SRC=Path(__file__).resolve().parent
ARCHIVE='Microduck-Robotd-FT6-R17.tar.gz'
BUILD='1fa8438-feetech-ft6-control.37'
VERSION='1.0.160'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def content_hash(raw):return hashlib.sha256(raw).hexdigest()

def write_json(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def files_in(root):
    return sorted((p for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc'),key=lambda p:p.relative_to(root).as_posix())

def verify_native(path, previous, name):
    path=Path(path)
    if not path.is_file() or not path.stat().st_size>500000 or digest(path)==digest(previous):
        raise ValueError(f'{name}: 没有新编译的 ARM64 程序；拒绝把 control.36 冒充 control.37')
    raw=path.read_bytes()
    if raw[:4]!=b'\x7fELF' or raw[4]!=2 or raw[5]!=1 or int.from_bytes(raw[18:20],'little')!=183:
        raise ValueError(f'{name}: 编译目标不是 Linux AArch64')
    if name=='robotd' and b'1fa8438-feetech-ft6-control.37' not in raw:
        raise ValueError('robotd: 未包含 control.37 构建标识')

def read_elf(path,existing):
    obj=dict(existing)
    obj['bytes']=path.stat().st_size
    obj['sha256']=digest(path)
    import subprocess
    if shutil.which('readelf'):
        dynamic=subprocess.run(['readelf','-d',str(path)],capture_output=True,text=True,check=True).stdout
        deps=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
        obj['needed']=deps
        versions=subprocess.run(['readelf','-V',str(path)],capture_output=True,text=True,check=True).stdout
        obj['glibc_versions']=sorted(set(re.findall(r'GLIBC_(\d+\.\d+)',versions)),key=lambda s:tuple(map(int,s.split('.'))))
        if any(tuple(map(int,x.split('.')))> (2,41) for x in obj['glibc_versions']):
            raise ValueError(f'{path.name}: 链接到了比 Zero 的 glibc 2.41 更新的 ABI')
    return obj

def validate_base_zip(path):
    if digest(path) != '2658193fe4be4d82ceedca60623e5217334cf19baf301939bb3cff88dcce3856':
        raise ValueError('必须使用指定的 Microduck-Console-R17-V159.zip；保留已确认的标定及中控修复')
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        roots={x.split('/')[0] for x in names if x}
        if len(roots)!=1: raise ValueError('V159 压缩包根目录不唯一')
        root=next(iter(roots))
        b=json.loads(z.read(root+'/BUILD_MANIFEST.json'))
        if b['console_version']!='1.0.159' or b['service_build']!='1fa8438-feetech-ft6-control.36':
            raise ValueError('基础中控或固件不是 V159/control.36')
        if content_hash(z.read(f'{root}/updates/{ARCHIVE}'))!=b['service_package_sha256']:
            raise ValueError('V159 随包固件原本校验失败')
        return root

def extract_trusted_zip(zip_path, temp_dir):
    with zipfile.ZipFile(zip_path) as z:
        for row in z.infolist():
            path=Path(row.filename)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('source zip invalid path')
        z.extractall(temp_dir)

def extract_trusted_tar(data, temp_dir):
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:
        for row in t:
            path=Path(row.name)
            if path.is_absolute() or '..' in path.parts or not row.isfile():
                raise ValueError('V159 tar contains unexpected entry')
        t.extractall(temp_dir,filter='data')

def build(args):
    base_root=validate_base_zip(args.base)
    test_log=SRC/'verification/v160/rust-tests.log'
    build_log=SRC/'verification/v160/arm64-build.log'
    test_text=test_log.read_text()
    test_record=json.loads((SRC/'verification/v160/rust-tests.json').read_text())
    release_record=json.loads((SRC/'verification/v160/release-tests.json').read_text())
    if release_record['failed'] or release_record['passed']<225:
        raise ValueError('本版控制/协议/手柄单元测试与滑轮测试未通过')
    results=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',test_text)
    if not results:
        raise ValueError('缺少本版 Rust 测试记录')
    if test_record['failed'] and not args.allow_test_failures:
        raise ValueError('历史全工程测试含失败；须显式保留原始记录，不得将它们写为通过')
    roller_log=SRC/'verification/v160/roller-tests.log'
    if 'test result: ok. 3 passed; 0 failed;' not in roller_log.read_text():
        raise ValueError('滑轮航向、原行走保持及完整模型配置测试未通过')
    model_record=json.loads((SRC/'verification/v160/arm64-models.json').read_text())
    if len(model_record['results'])!=3 or any(x['exit_code'] for x in model_record['results']):
        raise ValueError('三个滑轮模型的 ARM64 加载验证未通过')
    if not re.search(r'Finished `release` profile',build_log.read_text()):
        raise ValueError('缺少本版成功的 ARM64 release 构建记录')
    with tempfile.TemporaryDirectory(prefix='microduck-v160-') as temporary:
        temp=Path(temporary)
        extract_trusted_zip(args.base,temp)
        console=temp/base_root
        # V159 owns the authorized calibration, SSH credential fix and GitHub
        # entrances. Inherit those files directly, without rolling them back.
        with zipfile.ZipFile(args.base) as z: data=z.read(f'{base_root}/updates/{ARCHIVE}')
        nested=temp/'native';nested.mkdir()
        extract_trusted_tar(data,nested)
        fw=nested/'Microduck-Robotd-FT6-R17'
        for name,binpath in [('robotd',args.robotd),('padd',args.padd)]:
            verify_native(binpath,fw/name,name)
            shutil.copy2(binpath,fw/name)
            (fw/name).chmod(0o755)
        # No service/config changes: copy only changed native deployment allowlist,
        # model-owned files and release identity from matching source.
        for name in ('package-preflight.py','release_identity.py','install-files.json','README.zh-CN.md'):
            shutil.copy2(SRC/'packaging'/name,fw/name)
        for model in ('swizzle','crouch','spin'):
            shutil.copytree(SRC/'packaging/roller'/model,fw/'roller'/model)
        fw_manifest=json.loads((fw/'BUILD.json').read_text())
        if fw_manifest.get('build')!='1fa8438-feetech-ft6-control.36':
            raise ValueError('基础固件不匹配')
        fw_manifest.update(build=BUILD,console_version=VERSION,
            source_distribution='Microduck-Source-R17-V160-control37-compiled.tar.gz',
            release_changes='V160: true native control.37; physical DPad-Up walk/roller, physical DPad-Left 2s crouch/spin, IMU heading-error adapter; original walking unaffected',
            native_production_changes=['robotd/src/roller.rs','robotd/src/main.rs','duck-control/src/deployment.rs','duck-ipc-proto/src/lib.rs','padd/src/main.rs'],
            roller_modes={'swizzle':'roller/swizzle/policy.onnx','crouch':'roller/crouch/policy.onnx','spin':'roller/spin/policy.onnx'},
            hardware_verified=False,firmware_reinstall_required=True,
            release_status='compiled-unverified-hardware',
            package_baseline={'name':Path(args.base).name,'sha256':digest(args.base),
                'calibration':'user-authorized V159 calibration; preserved byte-for-byte'},
            regression_tests={'passed':test_record['passed'],'failed':test_record['failed'],'ignored':test_record['ignored']},
            release_scope_tests={'passed':release_record['passed'],'failed':release_record['failed'],
                'scope':release_record['selected_scope']},
            generated_at_utc=datetime.now(timezone.utc).isoformat())
        fw_manifest['rebuilt_binaries']=['robotd','padd']
        fw_manifest['reused_binaries']=sorted(set(fw_manifest.get('built_binaries',{}))-{'robotd','padd'})
        binaries=fw_manifest.get('built_binaries',{})
        for name in ('robotd','padd'):
            binaries[name]=read_elf(fw/name,binaries.get(name,{}))
        fw_manifest['padd_source_sha256']=digest(SRC/'padd/src/main.rs')
        write_json(fw/'BUILD.json',fw_manifest)
        elf=json.loads((fw/'ELF-CHECK.json').read_text())
        for name in ('robotd','padd'):
            elf[name]=read_elf(fw/name,elf[name])
        write_json(fw/'ELF-CHECK.json',elf)
        inventory=json.loads((fw/'install-files.json').read_text())
        required=[str(x.relative_to(fw).as_posix()) for x in files_in(fw) if x.name!='SHA256SUMS']
        missed=sorted(set(required)-set(inventory)-{'install-files.json'})
        # Existing package may contain transient files not owned by installed service:
        # only files listed in inventory are the recognized shipping surface.
        if missed:
            raise ValueError(f'固件随包文件未列入安装清单: {missed[:8]}')
        if sorted(set(inventory)) != sorted(inventory):
            raise ValueError('固件安装清单含重复文件')
        if not all((fw/x).is_file() for x in inventory):
            raise ValueError('固件安装清单有不存在的文件')
        lines=[f'{digest(fw/name)}  {name}' for name in sorted(set(inventory)|{'install-files.json'})]
        (fw/'SHA256SUMS').write_text('\n'.join(lines)+'\n')
        # Check ELF structure with shipped validator before producing any release.
        import importlib.util
        spec=importlib.util.spec_from_file_location('elf_check',fw/'elf_integrity.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        native_check=module.validate_bundle(fw)
        if native_check['robotd']['machine']!='AArch64' or native_check['padd']['machine']!='AArch64':
            raise ValueError('native ELF validation failed')
        # Prevent false build identity: validate native declaration and every file hash.
        for line in (fw/'SHA256SUMS').read_text().splitlines():
            sha,sep,name=line.partition('  ')
            if not sep or digest(fw/name)!=sha:raise ValueError('firmware digest mismatch '+name)
        arch=console/'updates'/ARCHIVE
        with tarfile.open(arch,'w:gz') as tar:
            for file in files_in(fw):
                arc=f'Microduck-Robotd-FT6-R17/{file.relative_to(fw).as_posix()}'
                tar.add(file,arcname=arc,recursive=False)
        # Re-open tar, check all content and the 64-MiB console upload limit.
        if arch.stat().st_size>32*1024*1024:
            raise ValueError('native firmware archive too big for original console upload gate')
        with tarfile.open(arch,'r:gz') as tar:
            if len(tar.getmembers())<110:raise ValueError('incomplete native package')
        version=console/'release_identity.py'
        raw=version.read_text()
        assert "CONSOLE_VERSION = '1.0.159'" in raw
        raw=raw.replace("CONSOLE_VERSION = '1.0.159'","CONSOLE_VERSION = '1.0.160'")
        raw=raw.replace('1fa8438-feetech-ft6-control.36',BUILD)
        version.write_text(raw)
        # Ship the current reference guide directly; never append a changelog to
        # the older console guide or retain its inactive roller description.
        shutil.copy2(SRC/'console/README.zh-CN.md',console/'README.zh-CN.md')
        # Remove former inactive experimental copies now that models live inside firmware.
        unused=console/'experiments'/'roller'
        if unused.exists():shutil.rmtree(unused)
        if (console/'experiments').exists() and not any((console/'experiments').iterdir()):
            (console/'experiments').rmdir()
        out_manifest=console/'BUILD_MANIFEST.json'
        meta=json.loads(out_manifest.read_text())
        meta.update(console_version=VERSION,service_build=BUILD,
            service_package_sha256=digest(arch),
            source_distribution='Microduck-Source-R17-V160-control37-compiled.tar.gz',
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            release_changes='V160: V159 baseline with user-authorized calibration, SSH credential fix and Github entrances preserved; native control.37 physical wheel mode and 3 policies',
            release_status='compiled-unverified-hardware',
            package_baseline=fw_manifest['package_baseline'],
            hardware_verified=False,firmware_reinstall_required=True,
            roller_experiment={'installed':True,'active':'physical-gamepad-only','models':['swizzle','crouch','spin']})
        logs=[]
        for source in (test_log,build_log,SRC/'verification/v160/rust-tests.json',roller_log,SRC/'verification/v160/arm64-models.json',SRC/'verification/v160/release-tests.log',SRC/'verification/v160/release-tests.json'):
            relative='verification/v160/'+source.name
            destination=console/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,destination)
            logs.append({'path':relative,'sha256':digest(destination)})
        meta['baseline_tests_run_in_release']=meta.pop('tests_run_in_release')
        meta['tests_run_in_release']={
            'robot_hardware_tested':False,
            'rust_passed':test_record['passed'],
            'rust_failed':test_record['failed'],
            'rust_ignored':test_record['ignored'],
            'full_regression_passed':not bool(test_record['failed']),
            'release_scope_passed':True,
            'release_scope_rust_passed':release_record['passed'],
            'release_scope_description':release_record['selected_scope'],
            'roller_tests_passed':3,
            'arm64_model_loads_passed':3,
            'rust_scope':['duck-control','duck-ipc-proto','robotd','padd'],
            'arm64_release_compiled':True,
            'logs':logs,
        }
        meta['files']=[{'path':str(p.relative_to(console).as_posix()),'bytes':p.stat().st_size,'sha256':digest(p)}
                       for p in files_in(console) if p!=out_manifest]
        write_json(out_manifest,meta)
        # Check console firmware manifest matches actual nested artifact.
        if digest(arch)!=meta['service_package_sha256'] or meta['service_build']!=BUILD:
            raise ValueError('console service digest not updated')
        output=Path(args.output).resolve()
        output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for file in files_in(console):
                z.write(file,arcname=f'Microduck-Console-R17-V160/{file.relative_to(console).as_posix()}')
        with zipfile.ZipFile(output) as z:
            err=z.testzip()
            if err:raise ValueError('outer ZIP CRC failed: '+err)
        print(f'V160 control.37 COMPLETED: {output} ({output.stat().st_size} bytes)')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--robotd',type=Path,required=True)
    parser.add_argument('--padd',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--allow-test-failures',action='store_true',help='保留历史全工程失败记录；不将失败计为通过，也不表示已通过实机验收')
    args=parser.parse_args()
    try:build(args)
    except Exception as exc:
        print('V160 打包拒绝：'+str(exc),file=sys.stderr)
        sys.exit(1)
