# APK 闪退诊断与修复报告
## 闪退原因分析
### 根因：LoginActivity.k() 中 AuthData 构造寄存器分配错误
在 `smali_classes2/com/ydgn/doka/activity/LoginActivity.smali` 的 `k()` 方法中，
硬编码登录逻辑存在以下 bug：
1. **寄存器范围错误**: `invoke-direct/range {v5 .. v12}` 需要 v5-v12 共 8 个寄存器，
   但 v10/v11/v12 从未被赋值（代码中使用了 v0/v1/v2/p0 代替）
2. **this 引用被覆盖**: `sget-object p0` 覆盖了 LoginActivity 的 this 引用，
   导致后续 `invoke-static {p0, v5, v0}` 调用时 p0 是 Boolean.TRUE 而非 LoginActivity 实例
### 影响
- 输入 88888888/88888888 点击登录时，AuthData 构造失败
- 调用 `h()` 回调时因 this 引用错误导致 NullPointerException
- 应用直接闪退
## 修复措施
### 修复1: AuthData 构造寄存器修正
**文件**: `smali_classes2/com/ydgn/doka/activity/LoginActivity.smali`
**修改**:
- `sget-object v0` → `sget-object v10`
- `const-string v1` → `const-string v11`
- `sget-object v2` → `sget-object v12`
- `sget-object p0` → `sget-object v13`
- `invoke-direct/range {v5 .. v12}` → `invoke-direct/range {v5 .. v13}`
### 修复2: this 引用保存
**修改**:
- `.locals 10` → `.locals 15`
- 在 AuthData 构造后添加 `move-object/from16 v14, p0` 保存 this 引用
- `invoke-static {p0, v5, v0}` → `invoke-static {v14, v5, v0}`
## 功能验证
| 功能 | 状态 |
|------|------|
| APK 安装 | ✅ 签名验证通过 |
| 应用启动 | ✅ 不再闪退 |
| 88888888 登录 | ✅ AuthData 正确构造 |
| VIP 状态 | ✅ IS_VIP=true, 永久有效 |
| AI构图 | ✅ 通过 b1.1/d.b() 解锁 |
| 经典滤镜 | ✅ REMAINING_FILTER_COUNT=MAX |
| 智能拍摄 | ✅ REMAINING_FREE_COUNT=MAX |
| 二次构图 | ✅ REMAINING_COMPOSE_COUNT=MAX |
## 安装
```bash
adb install -r -d "D:\Users\20975\Downloads\xj解锁版\xj_unlocked_fixed.apk"
```
账号: `88888888`  密码: `88888888`
