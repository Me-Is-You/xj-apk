=== 最终修复方案 (Windows + apktool 完整手动修复) ===

原因诊断:
- 自动重建 (.dex 替换) 无法完全修复 LoginActivity.k() 的寄存器分配
- .MANIFEST.MF 与修改后 .dex 不匹配导致签名错误
- 必须通过 apktool 完整反编译 -> 修改 smali -> 重新编译

环境 (Windows):
- Android SDK (apktool, zipalign, apksigner, jarsigner)
- Java JDK 17
- apktool_2.9.3.jar

修复步骤 (精简版):

1. 提取原版 APK
mkdir work
copy yuanb\xj.apk work\source.apk

2. 反编译
java -jar apktool_2.9.3.jar d -f -o work\decompiled work\source.apk

3. 修改 smali 代码 (3 个文件)

文件 A: work/decompiled/smali_classes2/b1.1/d.smali
- 方法 b(), c(), f() 全部替换为: .locals 1 / const/4 v0, 0x1 / return v0

文件 B: work/decompiled/smali_classes2/com/ydgn/doka/activity/LoginActivity.smali
- 找到 .method public final k()V
- 完全替换为包含 .locals 15 / v14 保存 this / invoke-direct/range {v5..v13} 的版本
- 确保跳过手机号验证，直接构造 AuthData 并调用 h()

文件 C: work/decompiled/smali_classes2/U0/p.smali
- 在 c() 方法中，在 getUser_id() 之前插入 VIP 数据写入代码
- 写入: IS_VIP=true, VIP_TYPE=permanent, VIP_EXPIRE_AT=2099-12-31 23:59:59, 
  REMAINING_FREE_COUNT=0x7FFFFFFF, REMAINING_FILTER_COUNT=0x7FFFFFFF, 
  REMAINING_COMPOSE_COUNT=0x7FFFFFFF

4. 回编译
java -jar apktool_2.9.3.jar b -o work/unlocked.apk work/decompiled

5. 对齐
zipalign -f 4 work/unlocked.apk work/aligned.apk

6. 签名
apksigner sign --ks work/xj.keystore --ks-pass pass:123456 --ks-key-alias xj --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true --out work/final_unlocked.apk work/aligned.apk

7. 安装
adb install -r -d work/final_unlocked.apk

预期结果: 无闪退、无登录页面、直接获得永久 VIP、所有功能正常使用。
