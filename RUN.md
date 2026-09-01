# راهنمای اجرای پروژه

## روش‌های اجرای پروژه

### 1. از Terminal (پیشنهادی)

```bash
# اجرای عادی
dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj

# اجرا با Watch Mode (تغییرات خودکار اعمال می‌شود)
dotnet watch run --project src/Identity/Identity.Api/Identity.Api.csproj
```

### 2. از VS Code

#### استفاده از Tasks:
1. `Ctrl+Shift+P` (یا `Cmd+Shift+P` در Mac)
2. تایپ کنید: `Tasks: Run Task`
3. یکی از گزینه‌های زیر را انتخاب کنید:
   - `run` - اجرای عادی
   - `watch` - اجرا با Watch Mode

#### استفاده از Terminal:
1. `Ctrl+`` (بک‌تیک) برای باز کردن Terminal
2. دستور زیر را اجرا کنید:
   ```bash
   dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
   ```

### 3. Build و سپس Run

```bash
# Build
dotnet build

# Run
cd src/Identity/Identity.Api
dotnet run
```

## دسترسی به API

پس از اجرای پروژه، می‌توانید از طریق آدرس‌های زیر به API دسترسی داشته باشید:

- **Swagger UI**: https://localhost:5001/swagger
- **API Base**: https://localhost:5001/api
- **HTTP**: http://localhost:5000

## نکات مهم

1. **Connection String**: در فایل `appsettings.json` تنظیم شده است
2. **JWT Secret Key**: در فایل `appsettings.json` تنظیم شده است
3. **Database**: به صورت خودکار Migration اجرا می‌شود

## عیب‌یابی

اگر خطایی دریافت کردید:

1. مطمئن شوید SQL Server در حال اجرا است
2. Connection String را بررسی کنید
3. پورت‌های 5000 و 5001 آزاد باشند
4. .NET SDK 8.0 یا بالاتر نصب باشد

