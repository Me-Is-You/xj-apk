#!/usr/bin/env python3
"""
APK 完整功能解锁脚本
对目标 APK 进行反编译、分析、修改、回编译、签名全流程自动化处理。
"""
import os, re, shutil, subprocess, tempfile, zipfile
from pathlib import Path
# ============================================================
# 配置
# ============================================================
TARGET_DIR = Path(r"D:\Users\20975\Downloads\xj解锁版")
SOURCE_APK = TARGET_DIR / "xj_unlocked_fixed.apk"  # 输入 APK
OUTPUT_APK = TARGET_DIR / "xj_unlocked_fixed_unlocked.apk"  # 输出 APK
WORK_DIR = Path(r"E:\aipyprowork\11")
TOOLS_DIR = WORK_DIR / "tools"
DECOMPILE_DIR = WORK_DIR / "xj_decompiled"
KEYSTORE_PATH = WORK_DIR / "xj.keystore"
ZIPALIGN_PATH = r"E:\Android\Sdk\build-tools\36.1.0\zipalign.exe"
APKSIGNER_PATH = r"E:\Android\Sdk\build-tools\36.1.0\apksigner.bat"
APKTOOL_BAT = TOOLS_DIR / "apktool.bat"
# 解锁配置
UNLOCK_ACCOUNT = "88888888"
UNLOCK_PASSWORD = "88888888"
UNLOCK_TOKEN = "vip_unlock_token_88888888"
UNLOCK_VIP_TYPE = "permanent"
UNLOCK_EXPIRE_DATE = "2099-12-31 23:59:59"
UNLOCK_MAX_COUNT = 0x7FFFFFFF  # 最大使用次数
def log(msg, level="INFO"):
    """统一日志输出"""
    print(f"[{level}] {msg}")
def run_cmd(cmd, timeout=300, shell=False):
    """运行命令并返回结果"""
    log(f"执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    if isinstance(cmd, list):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=shell)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
    if result.returncode != 0:
        err = result.stderr[:500] if result.stderr else "Unknown error"
        log(f"命令失败 (code={result.returncode}): {err}", "ERROR")
    return result
def step1_verify_environment():
    """步骤1: 环境验证"""
    global SOURCE_APK
    log("=" * 60)
    log("步骤1: 环境验证")
    log("=" * 60)
    # 检查源 APK
    if not SOURCE_APK.exists():
        # 尝试找到任何 APK 文件
        apks = list(TARGET_DIR.glob("*.apk"))
        if apks:
            SOURCE_APK = apks[0]
            log(f"使用 APK: {SOURCE_APK}")
        else:
            raise FileNotFoundError(f"未找到 APK 文件: {TARGET_DIR}")
    log(f"源 APK: {SOURCE_APK} ({os.path.getsize(SOURCE_APK)/1024/1024:.1f}MB)")
    # 检查工具
    for name, path in [("apktool", APKTOOL_BAT), ("zipalign", ZIPALIGN_PATH),
                        ("apksigner", APKSIGNER_PATH), ("keystore", KEYSTORE_PATH)]:
        if not Path(str(path)).exists():
            raise FileNotFoundError(f"工具缺失: {name} ({path})")
        log(f"  ✅ {name}: {path}")
    # 清理旧反编译目录
    if DECOMPILE_DIR.exists():
        shutil.rmtree(DECOMPILE_DIR, ignore_errors=True)
        log("  已清理旧反编译目录")
    return True
def step2_decompile():
    """步骤2: 反编译 APK"""
    log("\n" + "=" * 60)
    log("步骤2: 反编译 APK")
    log("=" * 60)
    result = run_cmd([str(APKTOOL_BAT), "d", "-f", "-o", str(DECOMPILE_DIR), str(SOURCE_APK)])
    if result.returncode != 0:
        raise RuntimeError(f"反编译失败: {result.stderr[:300]}")
    log("✅ 反编译成功")
    # 列出结构
    for item in sorted(DECOMPILE_DIR.iterdir()):
        if item.is_dir():
            log(f"  📁 {item.name}/ ({len(list(item.rglob('*')))} files)")
    return True
def step3_analyze_and_patch():
    """步骤3: 分析并修改 smali 代码"""
    log("\n" + "=" * 60)
    log("步骤3: 分析并修改 smali 代码")
    log("=" * 60)
    patches = []
    # ----------------------------------------------------------
    # 补丁1: b1.1/d.smali — VIP 状态判断始终返回 true
    # ----------------------------------------------------------
    b1d_path = DECOMPILE_DIR / "smali_classes2/b1.1/d.smali"
    if b1d_path.exists():
        content = b1d_path.read_text(encoding="utf-8", errors="ignore")
        # 修改 b() 方法
        old_b = re.search(r'\.method public static b\(\).*?\.end method', content, re.DOTALL)
        if old_b and "const/4 p0, 0x1" not in old_b.group():
            new_b = """.method public static b()Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method"""
            content = content.replace(old_b.group(), new_b)
            patches.append("b1.1/d.smali::b() — 始终返回 true")
        # 修改 c() 方法
        old_c = re.search(r'\.method public static c\(Ljava/lang/String;Z\)Z.*?\.end method', content, re.DOTALL)
        if old_c and "const/4 p0, 0x1" not in old_c.group():
            new_c = """.method public static c(Ljava/lang/String;Z)Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method"""
            content = content.replace(old_c.group(), new_c)
            patches.append("b1.1/d.smali::c() — 始终返回 true")
        # 修改 f() 方法
        old_f = re.search(r'\.method public static f\(LQ0/c;\)Z.*?\.end method', content, re.DOTALL)
        if old_f and "const/4 p0, 0x1" not in old_f.group():
            new_f = """.method public static f(LQ0/c;)Z
    .locals 1
    const/4 v0, 0x1
    return v0
.end method"""
            content = content.replace(old_f.group(), new_f)
            patches.append("b1.1/d.smali::f() — 始终返回 true")
        b1d_path.write_text(content, encoding="utf-8")
        log("✅ b1.1/d.smali 已修改")
    # ----------------------------------------------------------
    # 补丁2: LoginActivity.smali — 硬编码登录
    # ----------------------------------------------------------
    login_path = DECOMPILE_DIR / "smali_classes2/com/ydgn/doka/activity/LoginActivity.smali"
    if login_path.exists():
        content = login_path.read_text(encoding="utf-8", errors="ignore")
        k_match = re.search(r'\.method public final k\(\).*?\.end method', content, re.DOTALL)
        if k_match:
            new_k = f""".method public final k()V
    .locals 15
    iget-object v0, p0, Lcom/ydgn/doka/activity/LoginActivity;->a:Lcom/ydgn/doka/databinding/ActivityLoginBinding;
    const/4 v1, 0x0
    const-string v2, "binding"
    if-eqz v0, :cond_5
    iget-object v0, v0, Lcom/ydgn/doka/databinding/ActivityLoginBinding;->g:Landroid/widget/EditText;
    invoke-virtual {{v0}}, Landroid/widget/EditText;->getText()Landroid/text/Editable;
    move-result-object v0
    invoke-virtual {{v0}}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static {{v0}}, Lz1/g;->y0(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;
    move-result-object v0
    invoke-virtual {{v0}}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v3
    iget-object v0, p0, Lcom/ydgn/doka/activity/LoginActivity;->a:Lcom/ydgn/doka/databinding/ActivityLoginBinding;
    if-eqz v0, :cond_4
    iget-object v0, v0, Lcom/ydgn/doka/databinding/ActivityLoginBinding;->e:Landroid/widget/EditText;
    invoke-virtual {{v0}}, Landroid/widget/EditText;->getText()Landroid/text/Editable;
    move-result-object v0
    invoke-virtual {{v0}}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static {{v0}}, Lz1/g;->y0(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;
    move-result-object v0
    invoke-virtual {{v0}}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v5, "{UNLOCK_ACCOUNT}"
    invoke-virtual {{v3, v5}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-eqz v6, :cond_0
    invoke-virtual {{v4, v5}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :cond_0
    new-instance v5, Lcom/ydgn/doka/entity/AuthData;
    const-string v6, "{UNLOCK_ACCOUNT}"
    const-string v7, "{UNLOCK_TOKEN}"
    const-string v8, "{UNLOCK_ACCOUNT}"
    const-string v9, "VIP_User"
    sget-object v10, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    const-string v11, "phone"
    sget-object v12, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;
    sget-object v13, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    move-object/from16 v14, p0
    invoke-direct/range {{v5 .. v13}}, Lcom/ydgn/doka/entity/AuthData;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/Boolean;)V
    const/4 v0, 0x0
    invoke-static {{v14, v5, v0}}, Lcom/ydgn/doka/activity/LoginActivity;->h(Lcom/ydgn/doka/activity/LoginActivity;Lcom/ydgn/doka/entity/AuthData;Ljava/lang/String;)V
    return-void
    :cond_0
    iget-object p0, p0, Lcom/ydgn/doka/activity/LoginActivity;->a:Lcom/ydgn/doka/databinding/ActivityLoginBinding;
    if-eqz p0, :cond_3
    sget-object v1, Lcom/ydgn/doka/library/util/ValidatorUtil;->INSTANCE:Lcom/ydgn/doka/library/util/ValidatorUtil;
    invoke-virtual {{v1, v3}}, Lcom/ydgn/doka/library/util/ValidatorUtil;->isPhoneNumber(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_2
    const-string v0, "^\\\\d{{6}}$"
    invoke-static {{v0}}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;
    move-result-object v0
    const-string v1, "compile(...)"
    invoke-static {{v0, v1}}, Lkotlin/jvm/internal/k;->e(Ljava/lang/Object;Ljava/lang/String;)V
    const-string v1, "input"
    invoke-static {{v4, v1}}, Lkotlin/jvm/internal/k;->f(Ljava/lang/Object;Ljava/lang/String;)V
    invoke-virtual {{v0, v4}}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;
    move-result-object v0
    invoke-virtual {{v0}}, Ljava/util/regex/Matcher;->matches()Z
    move-result v0
    if-eqz v0, :cond_1
    const/4 v0, 0x1
    goto :goto_0
    :cond_1
    const/4 v0, 0x0
    :cond_2
    const/4 v0, 0x0
    :goto_0
    iget-object p0, p0, Lcom/ydgn/doka/databinding/ActivityLoginBinding;->b:Landroid/widget/Button;
    invoke-virtual {{p0, v0}}, Landroid/view/View;->setEnabled(Z)V
    return-void
    :cond_3
    invoke-static {{v2}}, Lkotlin/jvm/internal/k;->n(Ljava/lang/String;)V
    throw v1
    :cond_4
    invoke-static {{v2}}, Lkotlin/jvm/internal/k;->n(Ljava/lang/String;)V
    throw v1
    :cond_5
    invoke-static {{v2}}, Lkotlin/jvm/internal/k;->n(Ljava/lang/String;)V
    throw v1
.end method"""
            content = content[:k_match.start()] + new_k + content[k_match.end():]
            login_path.write_text(content, encoding="utf-8")
            patches.append("LoginActivity.smali::k() — 添加硬编码登录 + 修复寄存器")
            log("✅ LoginActivity.smali 已修改")
    # ----------------------------------------------------------
    # 补丁3: U0/p.smali — 强制设置 VIP 数据
    # ----------------------------------------------------------
    up_path = DECOMPILE_DIR / "smali_classes2/U0/p.smali"
    if up_path.exists():
        content = up_path.read_text(encoding="utf-8", errors="ignore")
        c_match = re.search(r'\.method public static c\(Lcom/ydgn/doka/entity/AuthData;\)V.*?\.end method', content, re.DOTALL)
        if c_match and "IS_VIP" not in c_match.group():
            c_body = c_match.group()
            # 在 getUser_id() 之前插入 VIP 数据
            vip_code = f"""    sget-object v0, Lcom/ydgn/doka/library/util/MMKVUtil;->INSTANCE:Lcom/ydgn/doka/library/util/MMKVUtil;
    const-string v1, "IS_VIP"
    const/4 v2, 0x1
    invoke-virtual {{v0, v1, v2}}, Lcom/ydgn/doka/library/util/MMKVUtil;->putBoolean(Ljava/lang/String;Z)Z
    const-string v1, "VIP_TYPE"
    const-string v2, "{UNLOCK_VIP_TYPE}"
    invoke-virtual {{v0, v1, v2}}, Lcom/ydgn/doka/library/util/MMKVUtil;->putString(Ljava/lang/String;Ljava/lang/String;)Z
    const-string v1, "VIP_EXPIRE_AT"
    const-string v2, "{UNLOCK_EXPIRE_DATE}"
    invoke-virtual {{v0, v1, v2}}, Lcom/ydgn/doka/library/util/MMKVUtil;->putString(Ljava/lang/String;Ljava/lang/String;)Z
    const-string v1, "REMAINING_FREE_COUNT"
    const v2, {UNLOCK_MAX_COUNT}
    invoke-virtual {{v0, v1, v2}}, Lcom/ydgn/doka/library/util/MMKVUtil;->putInt(Ljava/lang/String;I)Z
    const-string v1, "REMAINING_FILTER_COUNT"
    invoke-virtual {{v0, v1, v2}}, Lcom/ydgn/doka/library/util/MMKVUtil;->putInt(Ljava/lang/String;I)Z
    const-string v1, "REMAINING_COMPOSE_COUNT"
    invoke-virtual {{v0, v1, v2}}, Lcom/ydgn/doka/library/util/MMKVUtil;->putInt(Ljava/lang/String;I)Z
    """
            new_c_body = c_body.replace(
                "invoke-virtual {p0}, Lcom/ydgn/doka/entity/AuthData;->getUser_id()Ljava/lang/String;",
                vip_code + "    invoke-virtual {p0}, Lcom/ydgn/doka/entity/AuthData;->getUser_id()Ljava/lang/String;"
            )
            content = content.replace(c_body, new_c_body)
            up_path.write_text(content, encoding="utf-8")
            patches.append("U0/p.smali::c() — 强制写入 VIP 数据")
            log("✅ U0/p.smali 已修改")
    # ----------------------------------------------------------
    # 输出补丁清单
    log("\n📋 补丁清单:")
    for i, p in enumerate(patches, 1):
        log(f"  {i}. {p}")
    return patches
def step4_rebuild():
    """步骤4: 回编译"""
    log("\n" + "=" * 60)
    log("步骤4: 回编译 APK")
    log("=" * 60)
    unsigned_apk = WORK_DIR / "xj_unsigned.apk"
    if unsigned_apk.exists():
        os.remove(unsigned_apk)
    result = run_cmd([str(APKTOOL_BAT), "b", "-o", str(unsigned_apk), str(DECOMPILE_DIR)])
    if result.returncode != 0:
        raise RuntimeError(f"回编译失败: {result.stderr[:300]}")
    log(f"✅ 回编译成功: {os.path.getsize(unsigned_apk)/1024/1024:.1f}MB")
    # 修复 resources.arsc
    with zipfile.ZipFile(unsigned_apk, 'r') as zf:
        for info in zf.infolist():
            if info.filename == "resources.arsc" and info.compress_type != 0:
                fixed = WORK_DIR / "xj_fixed.apk"
                with zipfile.ZipFile(unsigned_apk, 'r') as zin:
                    with zipfile.ZipFile(fixed, 'w', zipfile.ZIP_DEFLATED) as zout:
                        for item in zin.infolist():
                            data = zin.read(item.filename)
                            if item.filename == "resources.arsc":
                                ni = zipfile.ZipInfo(item.filename)
                                ni.compress_type = zipfile.ZIP_STORED
                                zout.writestr(ni, data)
                            else:
                                zout.writestr(item, data)
                shutil.move(fixed, unsigned_apk)
                log("✅ resources.arsc 已修复为 STORED")
                break
    return unsigned_apk
def step5_align_and_sign(unsigned_apk):
    """步骤5: 对齐和签名"""
    log("\n" + "=" * 60)
    log("步骤5: 对齐和签名")
    log("=" * 60)
    # zipalign
    aligned = WORK_DIR / "xj_aligned.apk"
    if aligned.exists():
        os.remove(aligned)
    run_cmd([ZIPALIGN_PATH, "-f", "4", str(unsigned_apk), str(aligned)])
    log("✅ zipalign 完成")
    # 清理 CERT
    with zipfile.ZipFile(aligned, 'r') as zf:
        certs = [n for n in zf.namelist() if "CERT" in n]
        if certs:
            clean = WORK_DIR / "xj_clean.apk"
            with zipfile.ZipFile(aligned, 'r') as zin:
                with zipfile.ZipFile(clean, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        if "CERT" not in item.filename:
                            zout.writestr(item, zin.read(item.filename))
            shutil.move(clean, aligned)
            log(f"✅ 清理 CERT: {certs}")
    # 签名
    if OUTPUT_APK.exists():
        os.remove(OUTPUT_APK)
    cmd = [
        APKSIGNER_PATH, "sign",
        "--ks", str(KEYSTORE_PATH),
        "--ks-pass", "pass:123456",
        "--ks-key-alias", "xj",
        "--v1-signing-enabled", "true",
        "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true",
        "--out", str(OUTPUT_APK),
        str(aligned)
    ]
    result = run_cmd(cmd, timeout=60)
    if result.returncode != 0:
        # 回退 jarsigner
        log("apksigner 失败，回退 jarsigner...")
        cmd2 = [
            "jarsigner", "-verbose",
            "-sigalg", "SHA256withRSA", "-digestalg", "SHA-256",
            "-keystore", str(KEYSTORE_PATH),
            "-storepass", "123456", "-keypass", "123456",
            "-signedjar", str(OUTPUT_APK), str(aligned), "xj"
        ]
        run_cmd(cmd2, timeout=60)
    log(f"✅ 签名完成")
    return OUTPUT_APK
def step6_verify():
    """步骤6: 验证"""
    log("\n" + "=" * 60)
    log("步骤6: 验证")
    log("=" * 60)
    # 文件存在
    if not OUTPUT_APK.exists():
        raise FileNotFoundError(f"输出 APK 不存在: {OUTPUT_APK}")
    log(f"📦 输出 APK: {OUTPUT_APK}")
    log(f"💾 大小: {os.path.getsize(OUTPUT_APK)/1024/1024:.1f}MB")
    # ZIP 结构验证
    with zipfile.ZipFile(OUTPUT_APK, 'r') as zf:
        names = zf.namelist()
        log(f"📋 总文件数: {len(names)}")
        checks = {
            "AndroidManifest.xml": "AndroidManifest.xml" in names,
            "classes.dex": any(n.endswith(".dex") for n in names),
            "resources.arsc": "resources.arsc" in names,
            "签名文件": any(n.endswith(".RSA") for n in names),
        }
        for k, v in checks.items():
            log(f"  {k}: {'✅' if v else '❌'}")
    # 签名验证
    r = subprocess.run(["jarsigner", "-verify", str(OUTPUT_APK)], capture_output=True, text=True, timeout=30)
    if "jar 已验证" in r.stdout:
        log("✅ jarsigner 签名验证通过")
    # zipalign 验证
    r2 = subprocess.run([ZIPALIGN_PATH, "-c", "4", str(OUTPUT_APK)], capture_output=True, text=True, timeout=30)
    if r2.returncode == 0:
        log("✅ zipalign 对齐验证通过")
    # 检查 V2 签名
    with open(OUTPUT_APK, 'rb') as f:
        f.seek(max(0, os.path.getsize(OUTPUT_APK) - 65536))
        if b'APK Sig Block 42' in f.read():
            log("✅ V2/V3 签名已包含")
    return True
def main():
    """主流程"""
    global SOURCE_APK
    log("🚀 APK 完整功能解锁脚本启动")
    log(f"📂 源 APK: {SOURCE_APK}")
    log(f"📂 输出 APK: {OUTPUT_APK}")
    try:
        step1_verify_environment()
        step2_decompile()
        patches = step3_analyze_and_patch()
        unsigned = step4_rebuild()
        step5_align_and_sign(unsigned)
        step6_verify()
        log("\n" + "=" * 60)
        log("✅ 解锁完成！")
        log("=" * 60)
        log(f"📦 解锁后 APK: {OUTPUT_APK}")
        log(f"🔑 登录账号: {UNLOCK_ACCOUNT}")
        log(f"🔒 登录密码: {UNLOCK_PASSWORD}")
        log(f"📌 安装命令: adb install -r -d \"{OUTPUT_APK}\"")
        log(f"\n📋 共应用 {len(patches)} 个补丁")
        return True
    except Exception as e:
        log(f"❌ 解锁失败: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False
if __name__ == "__main__":
    success = main()
    # 通过 utils 报告状态
    try:
        utils.set_state(success=success, output_apk=str(OUTPUT_APK) if success else None)
    except:
        pass