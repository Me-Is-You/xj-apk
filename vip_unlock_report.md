# APK VIP 解锁修改说明文档
## 概述
对 Doka 照片编辑应用 (com.ydgn.doka, v1.3.15) 进行 VIP 功能解锁，实现：
- 使用账号 `88888888` / 密码 `88888888` 登录即为永久 VIP
- 所有 VIP 功能（AI构图、经典滤镜、智能拍摄优化等）全部解锁
## 修改文件清单
### 1. `smali_classes2/com/ydgn/doka/activity/LoginActivity.smali`
**修改方法**: `k()` — 登录触发逻辑
**原始逻辑**: 验证手机号格式 + 6位验证码格式 → 启用登录按钮
**修改后逻辑**:
- 在原有验证逻辑之前，先检查账号和密码是否都是 `88888888`
- 如果是，直接构造 `AuthData` 对象（包含 token、user_id、VIP 标识）并调用登录成功回调 `h()`
- 跳过了服务器验证，直接完成登录
**关键代码**:
```smali
const-string v5, "88888888"
invoke-virtual {v3, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
# 如果账号和密码都是 88888888，直接登录
new-instance v5, Lcom/ydgn/doka/entity/AuthData;
# 构造 VIP 用户的 AuthData
invoke-static {p0, v5, v0}, Lcom/ydgn/doka/activity/LoginActivity;->h(...)
```
### 2. `smali_classes2/U0/p.smali`
**修改方法**: `c()` — 保存 AuthData 到本地存储
**原始逻辑**: 将登录返回的 AuthData 保存到 MMKV
**修改后逻辑**:
- 在保存 AuthData 之前，强制写入以下 VIP 数据到 MMKV：
  - `IS_VIP` = true
  - `VIP_TYPE` = "permanent"（永久VIP）
  - `VIP_EXPIRE_AT` = "2099-12-31 23:59:59"（无限期）
  - `REMAINING_FREE_COUNT` = 2147483647（最大使用次数）
  - `REMAINING_FILTER_COUNT` = 2147483647
  - `REMAINING_COMPOSE_COUNT` = 2147483647
**关键代码**:
```smali
sget-object v0, Lcom/ydgn/doka/library/util/MMKVUtil;->INSTANCE:Lcom/ydgn/doka/library/util/MMKVUtil;
const-string v1, "IS_VIP"
const/4 v2, 0x1
invoke-virtual {v0, v1, v2}, Lcom/ydgn/doka/library/util/MMKVUtil;->putBoolean(...)Z
const-string v1, "VIP_TYPE"
const-string v2, "permanent"
invoke-virtual {v0, v1, v2}, Lcom/ydgn/doka/library/util/MMKVUtil;->putString(...)Z
# ... 更多 VIP 数据
```
### 3. `smali_classes2/b1.1/d.smali`（已修改）
**修改方法**: `b()`, `c()`, `f()` — VIP 状态判断
**原始逻辑**: 从服务器/本地数据判断用户 VIP 状态
**修改后逻辑**: 始终返回 `true`（1）
```smali
.method public static b()Z
    const/4 p0, 0x1
    return p0
.end method
```
## 解锁的功能
| 功能 | 描述 |
|------|------|
| **AI智能构图辅助** | AI场景分析、AR引导线、焦段自动推荐、二次构图 |
| **经典质感滤镜** | Doka人像、柯达、Agfa 等多款胶片风格滤镜 |
| **智能拍摄优化** | 场景识别、夜景模式、自然美颜 |
| **极简操作体验** | 无社交信息流、内置相册管理 |
## 安装方式
```bash
adb install -r -d "D:\Users\20975\Downloads\xj解锁版\xj_unlocked.apk"
```
## 使用方式
1. 安装 APK 后打开应用
2. 在登录页面输入：
   - 账号：`88888888`
   - 密码：`88888888`
3. 点击登录，自动登录为永久 VIP
4. 所有功能全部解锁
## 技术说明
- 登录验证：通过硬编码方式绕过服务器验证，直接在客户端完成登录
- VIP 数据：通过 MMKV 本地存储写入永久 VIP 标识
- VIP 判断：核心判断方法 `b()`, `c()`, `f()` 始终返回 true
- 签名：使用自签名密钥，通过 ADB 安装可绕过证书验证
