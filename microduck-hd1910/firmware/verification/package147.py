"""Build the v147 delivery from v146 payload bytes and current verification logs.

No robot, systemd service, uinput device, or external publication is operated here.
Run after native/frontend/input verification and the final ARM64 cross-build.
"""
from pathlib import Path
import contextlib
import datetime
import hashlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile

B = Path(__file__).resolve().parent
VERSION = '1.0.147'
BUILD = '1fa8438-feetech-ft6-control.30'
S = B / f'source/Microduck-Source-R17-v{VERSION}'
OLD = B.parent / 'work-r17-146/source/Microduck-Source-R17-v1.0.146'
OLD_STAGE = B.parent / 'work-r17-146/stage/Microduck-Robotd-FT6-R17'
STAGE = B / 'stage/Microduck-Robotd-FT6-R17'
OUT = B.parent / f'output/R17-v{VERSION}'
NATIVE = Path('/tmp/r17-native-target/aarch64-unknown-linux-gnu/release')
OLD_IDS = {'roulade': '8fdaf12c7478a8314a63647a466bfa34',
           'ground_pick': '2b69fa681ed06f7ded9e2a2d12ba5c67'}
UPLOADS = {'roulade': '前滚翻_10000_4096_无缩放滤波.zip',
           'ground_pick': '低头减取_10000_4096_无缩放滤波.zip'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def records(root, exclude=()):
    return [dict(path=str(p.relative_to(root)), bytes=p.stat().st_size, sha256=digest(p))
            for p in sorted(root.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and str(p.relative_to(root)) not in exclude]


def same_tree(a, b):
    ar, br = records(a), records(b)
    assert ar == br, (str(a), str(b))
    return len(ar)


def elf_record(path):
    header = subprocess.check_output(['readelf', '-h', str(path)], text=True)
    dynamic = subprocess.check_output(['readelf', '-d', str(path)], text=True)
    versions = subprocess.check_output(['readelf', '--version-info', str(path)], text=True)
    assert 'AArch64' in header, path
    glibc = sorted(set(re.findall(r'GLIBC_(\d+\.\d+)', versions)),
                   key=lambda v: tuple(map(int, v.split('.'))))
    assert glibc and max(tuple(map(int, v.split('.'))) for v in glibc) <= (2, 31)
    return dict(sha256=digest(path), machine='AArch64',
                needed=re.findall(r'Shared library: \[(.*?)\]', dynamic),
                glibc_versions=glibc, bytes=path.stat().st_size)


RUST_RESULT = re.compile(
    r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; '
    r'(\d+) measured; (\d+) filtered out;')


def native_summary(log):
    assert 'test result: FAILED.' not in log and 'error: test failed' not in log
    starts = list(re.finditer(r'Running unittests [^\n]*[/\\]([a-z0-9_]+)-[0-9a-f]+\)', log))
    suites = {}
    for i, start in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(log)
        results = list(RUST_RESULT.finditer(log[start.end():end]))
        assert results, start.group(1)
        passed, failed, ignored, measured, filtered = map(int, results[-1].groups())
        assert passed and not failed and not measured and not filtered
        suites[start.group(1)] = dict(passed=passed, failed=failed, ignored=ignored)
    assert 'robotd' in suites
    return suites


def python_summary(log):
    counts = re.findall(r'^Ran (\d+) tests? in ', log, re.M)
    result = re.search(r'^OK(?: \(skipped=(\d+)\))?\s*\Z', log, re.M)
    assert counts and result, 'Python unittest run did not finish successfully'
    total = int(counts[-1]); skipped = int(result.group(1) or 0)
    assert total > 0
    return dict(run=total, passed=total - skipped, skipped=skipped)


assert S.is_dir() and OLD.is_dir() and OLD_STAGE.is_dir()
suites=native_summary((B/'native-tests147.log').read_text())
python_result=python_summary((B/'python-tests147.log').read_text())
build_evidence=json.loads((B/'native-build-environment147.json').read_text())
assert build_evidence['exit_code']==0 and build_evidence['source_files_unchanged']
assert all(digest(S/name)==expected for name,expected in build_evidence['source_files_sha256'].items())
assert all(digest(NATIVE/name)==expected for name,expected in build_evidence['binary_sha256'].items())
assert set(build_evidence['binary_sha256'])=={'robotd','robotctl'}
evidence=json.loads((B/'focused-verification147.json').read_text())
assert evidence['all_passed']
tests=dict(python=python_result['passed'],python_run=python_result['run'],python_skipped=python_result['skipped'],
    native_suites=suites,focused=evidence,robotd_rebuilt=True,robotctl_rebuilt=True,padd_rebuilt=False,
    reused_binary_payload_from='1.0.146',hardware_tested=False,full_system_integration_verified=False,
    integration_scope='Real new ONNX models with synthetic inputs and fake hardware; target scale/filter/phase/return-to-Walk regressions; Python import and actual repeated payload upgrades. No robot motion, systemd/uinput activation or live GameSir test.')
log_names=['native-tests147.log','python-tests147.log','native-build147.log','native-build-environment147.json',
    'focused-verification147.json','action-model-audit147.json','action-model-audit147.txt',
    'audit_action_models147.py','restore_toolchain147.py','toolchain-restore147.json','build_native147.py']
for name in evidence['evidence_files']:
    if name not in log_names:log_names.append(name)
for name in log_names:assert (B/name).is_file(),name

OUT.mkdir(parents=True,exist_ok=True)
for cache in S.rglob('__pycache__'):shutil.rmtree(cache)
verification=S/'verification'
if verification.exists():shutil.rmtree(verification)
verification.mkdir()
for name in log_names:shutil.copy2(B/name,verification/name)
if (OLD/'verification/official-reference').exists():
    shutil.copytree(OLD/'verification/official-reference',verification/'official-reference-from146')
shutil.copy2(__file__,verification/'package147.py')

if STAGE.exists():shutil.rmtree(STAGE)
shutil.copytree(OLD_STAGE,STAGE)
for cache in STAGE.rglob('__pycache__'):shutil.rmtree(cache)
for name in json.loads((S/'packaging/install-files.json').read_text()):
    source=S/'packaging'/name
    if source.is_file():
        target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
for name in ['robotd','robotctl']:shutil.copy2(NATIVE/name,STAGE/name)
assert BUILD.encode() in (STAGE/'robotd').read_bytes()
assert (S/'console/release_identity.py').read_bytes()==(STAGE/'release_identity.py').read_bytes()
assert BUILD in (STAGE/'release_identity.py').read_text()
assert not (S/'console/remote_control.py').exists()

sys.path.insert(0,str(S/'packaging'))
from model_packages import verify_directory,catalog
from configure import dumps
new={slot:verify_directory(S/'policies'/slot) for slot in OLD_IDS}
preserved={'source_directories':{},'source_files':{},'payload_files':{},'uploaded_training_files':{},'legacy_fixtures':{}}
for slot,info in new.items():
    assert len(info['id'])==32 and info['id']==info['sha256'][:32]
    assert info['contract']['actions']['joint_pos']['scale']==1.0
    assert info['contract']['action_filter']['enabled'] is False
    assert info['contract']['action_filter']['head_alpha']==info['contract']['action_filter']['legs_alpha']==1.0
    assert 'execution_profile' not in info
    target=STAGE/'models'/info['id'];shutil.copytree(S/'policies'/slot,target,dirs_exist_ok=True)
    shutil.rmtree(STAGE/'models'/OLD_IDS[slot])
    legacy=S/'test-data'/('roulade-legacy' if slot=='roulade' else 'ground-pick-legacy')
    preserved['legacy_fixtures'][slot]=dict(files=same_tree(OLD/'policies'/slot,legacy),runtime_shipped=False)
    original=B.parent/'upload'/UPLOADS[slot]
    with zipfile.ZipFile(original) as z:
        assert z.testzip() is None
        for item in z.infolist():
            if item.is_dir() or item.filename=='checkpoint.pt':continue
            assert (target/item.filename).read_bytes()==z.read(item),item.filename
            preserved['uploaded_training_files'][slot+'/'+item.filename]=digest(target/item.filename)
    assert not (target/'checkpoint.pt').exists()
assert len([p for p in (STAGE/'models').iterdir() if p.is_dir()])==5

for directory in ['gamepad-r7','padd','robotctl','sounds','odometry','firmware','kinematics']:
    preserved['source_directories'][directory]=same_tree(OLD/directory,S/directory)
for slot in ['walk','stand','sitstand']:
    preserved['source_directories']['policies/'+slot]=same_tree(OLD/'policies'/slot,S/'policies'/slot)
for name in ['Cargo.lock','robotd/src/params.rs','robotd/src/intents.rs','robotd/src/home_start.rs',
             'robotd/src/raw_codec.rs','robotd/src/telemetry_system.rs','robotd/src/telemetry_geometry.rs',
             'console/static/duck.js','console/static/webpad-controls.js','console/static/raw-telemetry.js',
             'console/static/raw-kinematics.js','console/static/control-socket.js','console/raw_telemetry.py',
             'console/socket_transport.py','console/console.py','console/controls.py','console/control_socket.py']:
    assert digest(OLD/name)==digest(S/name),name
    preserved['source_files'][name]=digest(S/name)
for name in ['padd','sounds','uart-service.py','hd1910-calibration.robot.toml','hd1910-calibration.training.toml',
             'hd1910-calibration.template.toml','gamepad-r7/gamesir-xboxd','webpad.py','microduck-webpad.service','microduck-webpad.socket']:
    assert digest(OLD_STAGE/name)==digest(STAGE/name),name
    preserved['payload_files'][name]=digest(STAGE/name)
preserved['payload_models']={}
for directory in (OLD_STAGE/'models').iterdir():
    if not directory.is_dir():continue
    if directory.name in OLD_IDS.values():assert not (STAGE/'models'/directory.name).exists()
    else:preserved['payload_models'][directory.name]=same_tree(directory,STAGE/'models'/directory.name)
preserved['onnxruntime_files']=same_tree(OLD_STAGE/'onnxruntime',STAGE/'onnxruntime')
hat='console/updates/imu_to_feetech_ReVA_FT6_SYNC15_UART_IRQ_v1.bin'
assert digest(S/hat)==digest(OLD/hat);preserved['hat_firmware_sha256']=digest(S/hat)
assert digest(STAGE/'padd')=='78b456e7c19e720330c325fe16719e291d36373c0879911d59f77700d52f79a3'

elf={name:elf_record(STAGE/name) for name in ['robotd','robotctl','padd','sounds','gamepad-r7/gamesir-xboxd']}
build=json.loads((S/'BUILD.json').read_text())
build.update(build=BUILD,console_version=VERSION,api_version=40,source_distribution=S.name+'.tar.gz',
    generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    release_changes='Replace front roll and ground pick with the uploaded 10000-iteration/4096-env unfiltered models. Support modern flat Roulade and Flat-Backlash GroundPick contracts; one-time slot/scale migration and exact old-model cleanup. Preserve joint Walk, independent LB, calibration and 50Hz input/telemetry.',
    tests=tests,rebuilt_binaries=['robotd','robotctl'],reused_binaries=['padd','sounds','gamepad-r7/gamesir-xboxd'],
    toolchain='Rust 1.99.0, cargo-zigbuild 0.23.4 and Zig 0.14.1; aarch64-unknown-linux-gnu.2.31',
    built_binaries=elf,runtime_model_count=5,
    retired_action_model_ids=OLD_IDS,action_replacement_ids={slot:info['id'] for slot,info in new.items()})
build.pop('build_status',None)
for slot,info in new.items():
    build['models'][slot].update(id=info['id'],sha256=info['sha256'],task=info['task'],
        source_policy_directory='policies/'+slot,epochs=10000,source_iteration=9999,num_envs=4096,
        base_action_scale=1.0,target_filter='passthrough',head_alpha=1.0,legs_alpha=1.0,
        deployment_verified=False)
if 'manual_recovery_test' in build:
    build['manual_recovery_test'].update(existing_walk_preserved=True,requested_replacement=False)
    build['manual_recovery_test'].pop('walk_replacement_in_this_release',None)
build['model_specific_filter_selection_changed']=False
build['modern_unfiltered_action_contract_support']=dict(introduced_in=VERSION,backlash_format_independent=True,
    raw_training_files_unchanged=True,global_tuning_preserved=True,scale_migration_once=True,
    interrupted_config_migration_retried=True,new_high_frequency_work=False,physical_tested=False)
build['release_changed_native_source_files']=[r['path'] for r in records(S)
    if r['path'].startswith(('robotd/src/','duck-control/src/','duck-ipc-proto/src/','robotd-params/src/'))
    and (not (OLD/r['path']).is_file() or digest(OLD/r['path'])!=r['sha256'])]
test_only_native={'robotd/src/control.rs','robotd/src/selftrained_checks.rs'}
build['release_native_production_changes']=[name for name in build['release_changed_native_source_files']
    if not name.endswith('_tests.rs') and name not in test_only_native]
build['release_native_test_changes']=[name for name in build['release_changed_native_source_files']
    if name.endswith('_tests.rs') or name in test_only_native]
for meta in build['models'].values():assert verify_directory(STAGE/'models'/meta['id'])['sha256']==meta['sha256']
for root in [S,STAGE]:write(root/'BUILD.json',build);write(root/'ELF-CHECK.json',elf)
for cache in STAGE.rglob('__pycache__'):shutil.rmtree(cache)
write(STAGE/'install-files.json',[r['path'] for r in records(STAGE,['SHA256SUMS','install-files.json'])])
shutil.copy2(STAGE/'install-files.json',S/'packaging/install-files.json')
(STAGE/'SHA256SUMS').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in records(STAGE,['SHA256SUMS'])))

spec=importlib.util.spec_from_file_location('installer147',STAGE/'install-files.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
install_log=io.StringIO()
with contextlib.redirect_stdout(install_log):
    for preimported in [False,True]:
        with tempfile.TemporaryDirectory() as temporary:
            temp=Path(temporary);live=temp/'installed';shutil.copytree(OLD_STAGE,live)
            if preimported:
                for info in new.values():shutil.copytree(STAGE/'models'/info['id'],live/'models'/info['id'])
            before_models={p.name:records(p) for p in (live/'models').iterdir() if p.is_dir()}
            previous=temp/'old/robotd-profile.toml';replacement=temp/'new/robotd-profile.toml'
            for source,target in [(OLD_STAGE,previous),(STAGE,replacement)]:
                target.parent.mkdir();target.write_text((source/'robotd-profile.toml').read_text().replace('/opt/robot/feetech-ft5-r5',str(live)))
                shutil.copy2(source/'management-profile.json',target.with_name('management-profile.json'))
            cfg=temp/'robotd.toml';params=tomllib.loads(previous.read_text())
            params['policy'].update(action_scale=.63,head_lowpass=.41,legs_lowpass=.69,voltage_adapt=True,
                                    ground_pick_action_scale=.6,ground_pick_gain_ratio=.8)
            roll=next(s for s in params['policy']['skill'] if s['name']=='roulade')
            roll.update(path=params['policy']['roulade'],duration=1.4)
            roll['params'].update(action_scale=.5,gain_ratio=.9)
            next(s for s in params['policy']['skill'] if s['name']=='stand_test')['duration']=8.0
            cfg.write_text(dumps(params));expected=json.loads(json.dumps(params))
            for slot,info in new.items():expected['policy'][slot]=str(live/'models'/info['id']/'policy.onnx')
            expected['policy']['ground_pick_action_scale']=1.0
            roll=next(s for s in expected['policy']['skill'] if s['name']=='roulade')
            roll['path']=expected['policy']['roulade'];roll['params']['action_scale']=1.0
            operator={'hd1910-calibration.local.toml':(OLD_STAGE/'hd1910-calibration.robot.toml').read_bytes(),
                'servo-test-parameters.json':b'{"kp":5,"kd":20,"torque_limit":1000}',
                'pad-settings.json':b'{"mouth_percent":70,"head_rad":1.0}',
                'voice-device.json':b'{"card":"aic3104","operator_saved":true}'}
            for name,data in operator.items():(live/name).write_bytes(data)
            for attempt in range(2):
                next_cfg=temp/'next.toml'
                result=subprocess.run([sys.executable,str(STAGE/'configure.py'),'--source',str(cfg),
                    '--previous-overrides',str(previous),'--overrides',str(replacement),'--output',str(next_cfg)],
                    check=True,capture_output=True,text=True)
                print(result.stdout.strip());installer.install(STAGE,live);cfg.write_bytes(next_cfg.read_bytes())
                actual=tomllib.loads(cfg.read_text());assert actual==expected,'only requested action paths/scales may change'
                assert all((live/name).read_bytes()==data for name,data in operator.items())
                assert actual['control']['hz']==50
                for ident,before in before_models.items():
                    if ident in OLD_IDS.values():assert not (live/'models'/ident).exists()
                    else:assert records(live/'models'/ident)==before,ident
                for info in new.values():same_tree(STAGE/'models'/info['id'],live/'models'/info['id'])
                for name in ['robotd','robotctl','padd','release_identity.py','webpad.py']:assert digest(live/name)==digest(STAGE/name)
                listing=catalog(live,cfg)
                assert len(listing['models'])==5 and all(row['available'] for row in listing['models'])
                assert not set(OLD_IDS.values())&{row['id'] for row in listing['models']}
                assert listing['configured_model']==build['models']['walk']['id']
                assert sum(row['slot']=='walk' for row in listing['slots'])==1
                assert listing['manual_recovery']['model']['id']==build['models']['stand']['id']
                for slot,info in new.items():assert next(row for row in listing['slots'] if row['slot']==slot)['model']['id']==info['id']
                previous.write_bytes(replacement.read_bytes())
                previous.with_name('management-profile.json').write_bytes(replacement.with_name('management-profile.json').read_bytes())
            print(f'PASS actual v146-to-v147 payload twice; preimported={preimported}; two new actions, five models, old pair removed, sole Walk/LB/other original bytes, action timing/non-scale parameters, global tuning and calibration preserved.')
(verification/'payload-upgrade147.log').write_text(install_log.getvalue())

archive=S/'console/updates/Microduck-Robotd-FT6-R17.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=9) as tar:
    tar.add(STAGE,arcname=STAGE.name,filter=lambda item:None if '__pycache__' in Path(item.name).parts else item)
console=S/'console';manifest=json.loads((OLD/'console/BUILD_MANIFEST.json').read_text())
manifest.update(console_version=VERSION,service_build=BUILD,service_package_sha256=digest(archive),
    source_distribution=build['source_distribution'],tests_run_in_release=tests)
manifest.pop('build_status',None);manifest['files']=records(console,['BUILD_MANIFEST.json']);write(console/'BUILD_MANIFEST.json',manifest)
firmware_zip=OUT/f'Microduck-Firmware-R17-v{VERSION}.zip'
with zipfile.ZipFile(firmware_zip,'w',zipfile.ZIP_DEFLATED) as package:
    for path in [archive,STAGE/'README.zh-CN.md',STAGE/'BUILD.json',STAGE/'ELF-CHECK.json']:
        package.write(path,f'Microduck-Firmware-R17-v{VERSION}/'+path.name)
console_zip=OUT/f'Microduck-Console-R17-v{VERSION}.zip'
with zipfile.ZipFile(console_zip,'w',zipfile.ZIP_DEFLATED) as package:
    for record in records(console):package.write(console/record['path'],f'Microduck-Console-R17-v{VERSION}/'+record['path'])
sys.path.insert(0,str(console))
from firmware_packages import bundle_info,PreparedFirmware
assert bundle_info()['console_version']==VERSION
for package in [firmware_zip,console_zip]:
    with package.open('rb') as stream:
        prepared=PreparedFirmware(package.name,stream,package.stat().st_size,'release147-check')
        try:assert digest(prepared.path)==digest(archive)
        finally:prepared.close()

changed=[r['path'] for r in records(STAGE) if not (OLD_STAGE/r['path']).is_file() or digest(OLD_STAGE/r['path'])!=r['sha256']]
audit=dict(console_version=VERSION,service_build=BUILD,tests=tests,preserved=preserved,
    evidence=[dict(name=name,sha256=digest(B/name)) for name in log_names],changed_payload_files=changed,
    install_repeated_with_settings_preserved=True,preimported_model_preserved=True,
    old_actions_removed_on_ordinary_upgrade=True,only_one_walk_slot=True,runtime_models=5,
    console_and_firmware_import_verified=True,payload_sha256=digest(archive),rebuilt_binaries=['robotd','robotctl'],
    reused_padd_verified=True,api_version=40,raw_schema='r17.raw.v1',raw_envelope_changed=False,hardware_tested=False)
write(verification/'release-audit147.json',audit)
(verification/'REPRODUCE.txt').write_text('''Use Rust 1.99.0, cargo-zigbuild 0.23.4, Zig 0.14.1 and ONNX Runtime 1.28.0.
restore_toolchain147.py restores actual toolchains and records download SHA256.
PYTHONPATH="$PWD/packaging:$PWD/console" python3 -m unittest discover -s packaging -p 'test_*.py' -v
cargo test -p robotd --bin robotd --locked
cargo test -p duck-control --lib --locked
cargo test -p robotd-params -p duck-ipc-proto --lib --bins --locked
Cross-build: cargo zigbuild -p robotd -p robotctl --release --target aarch64-unknown-linux-gnu.2.31 --locked
build_native147.py hashes exact Rust/Cargo sources before/after compilation and records tools, logs and ARM binaries.
padd is reused from v146; API40, padd source and binary SHA are verified unchanged.
package147.py expects work-r17-146 as baseline and work-r17-147 with current source/logs, plus two original ZIPs in upload/.
It verifies all original model files byte-for-byte, preserves Walk/LB/sitstand, installs the real payload twice with/without preimported models, and imports both ZIP formats through PreparedFirmware.
Legacy roll/pick fixtures in source test-data are deliberately excluded from the runtime payload.
The official-reference-from146 directory is retained historical evidence, not a new official-source lookup.
checkpoint.pt is never deserialized or deployed. Synthetic model and fake-hardware tests do not establish physical behavior.
No Zero motion, real gamepad, systemd/uinput activation, browser rendering or temperature measurement this release.
''')
for cache in S.rglob('__pycache__'):shutil.rmtree(cache)
summary=json.loads((OLD/'R17-SOURCE-MANIFEST.json').read_text())
summary.update(console_version=VERSION,service_build=BUILD,
    release_changed_files=[r['path'] for r in records(S,['R17-SOURCE-MANIFEST.json','SHA256SUMS'])
        if not (OLD/r['path']).is_file() or digest(OLD/r['path'])!=r['sha256']],
    release_removed_files=[r['path'] for r in records(OLD) if not (S/r['path']).exists()],
    files=records(S,['R17-SOURCE-MANIFEST.json','SHA256SUMS']))
write(S/'R17-SOURCE-MANIFEST.json',summary)
(S/'SHA256SUMS').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in records(S,['SHA256SUMS'])))
source_archive=OUT/build['source_distribution']
with tarfile.open(source_archive,'w:gz',compresslevel=9) as tar:
    tar.add(S,arcname=S.name,filter=lambda item:None if '__pycache__' in Path(item.name).parts else item)
native_lines='\n'.join(f"- {name}: {result['passed']}通过，{result['ignored']}默认忽略。" for name,result in suites.items())
report=OUT/f'Microduck-R17-v{VERSION}-Changes-and-Verification.txt'
report.write_text((S/'README-R17.zh-CN.md').read_text()+'\n\n模型审计\n'+(B/'action-model-audit147.txt').read_text()+f'''

本轮发布验证
- Python: {python_result['run']}项运行，{python_result['passed']}通过，{python_result['skipped']}跳过。
{native_lines}
- 新动作真实 ONNX 的基础系数1、无目标滤波、原始 previous_action、GroundPick phase、技能结束回联合 Walk、LB入口和旧合同回归均在原生测试中验证。
- 前两轮既有PTY/IMU截止时间测试曾随主机调度负载失败；未修改时间门限或跳过测试，最后完整轮全部通过。原始失败与最终日志均保留，实机时序未因此获证。
- robotd 和 robotctl 已重新交叉编译为 AArch64，GLIBC 符号依赖不高于2.31；padd复用经过SHA核对的v146 API40二进制。
- 真正v146→v147载荷在临时目录验证两种路径，各连续安装两次：未导入新模型、已预先导入相同两模型。
- 两个旧动作目录删除；新动作基础scale从旧测试值.6/.5迁移为1；Walk/LB/起坐字节、全局.63/.41/.69、电压补偿、动作时长、非缩放调参、按键和本机标定保留。
- 中断安装后已更新默认配置但实际动作路径仍旧时，重装会重试路径及基础缩放迁移；同版完整升级后的用户新选择保留。
- 真实手柄桥、padd、HAT固件、ONNX Runtime及遥测/输入运行代码按SHA256保留。
- 两个交付ZIP通过生产导入器，内含同一个固件载荷。没有改动页面布局，没有增加高频计算或采集循环。
- 没有在Zero安装或执行运动，没有做实机温度、真实手柄、systemd/uinput或Chromium渲染验证。

前滚翻 ONNX SHA256: {new['roulade']['sha256']}
捡取 ONNX SHA256: {new['ground_pick']['sha256']}
固件载荷 SHA256: {digest(archive)}
robotd SHA256: {digest(STAGE/'robotd')}
robotctl SHA256: {digest(STAGE/'robotctl')}
padd SHA256: {digest(STAGE/'padd')}
''')
artifacts=[console_zip,firmware_zip,source_archive,report]
(OUT/f'SHA256SUMS-v{VERSION}.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in artifacts))
print(json.dumps(dict(build=BUILD,artifacts=[dict(name=p.name,bytes=p.stat().st_size,sha256=digest(p)) for p in artifacts],
    changed_payload_files=changed,artifacts_verified=True,hardware_tested=False),ensure_ascii=False,indent=2))


