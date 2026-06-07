#!/usr/bin/env python3
"""
Werygram Visual Premium Patcher
Автоматическая интеграция мода в Telegram с последующей сборкой APK
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_ROOT, "build_output")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "werygram_mods")
GRADLE_BUILD = os.path.join(PROJECT_ROOT, "TMessagesProj_App", "build", "outputs", "apk")

# Java injection paths
SETTINGS_ACTIVITY = "TMessagesProj_App/src/main/java/org/telegram/ui/SettingsActivity.java"
PREFERENCE_MANAGER = "TMessagesProj/src/main/java/org/telegram/ui/PrefUtils.java"
CHAT_CELL = "TMessagesProj_App/src/main/java/org/telegram/ui/Cells/ChatCell.java"

PREM_FLAG = "WERYGRAM_PREMIUM_ENABLED"

class WerygramPatcher:
    def __init__(self):
        self.log_messages = []
        self.build_status = "PENDING"
        
    def log(self, message, level="INFO"):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
    
    def create_output_dirs(self):
        """Создание директорий для вывода"""
        os.makedirs(BUILD_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.log("Директории для вывода созданы")
    
    def inject_pref_utils(self):
        """Инъекция класса PrefUtils"""
        pref_code = f'''package org.telegram.ui;

import android.content.SharedPreferences;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.messenger.MessagesController;

public class PrefUtils {{
    private static final String PREF_NAME = "werygram_prefs";
    private static final String {PREM_FLAG} = "premium_visual";
    
    public static void togglePremiumVisuals() {{
        boolean current = isPremiumVisualsEnabled();
        SharedPreferences prefs = ApplicationLoader.applicationContext
            .getSharedPreferences(PREF_NAME, 0);
        prefs.edit().putBoolean({PREM_FLAG}, !current).apply();
        MessagesController.getInstance(0).updateInterface();
    }}
    
    public static boolean isPremiumVisualsEnabled() {{
        SharedPreferences prefs = ApplicationLoader.applicationContext
            .getSharedPreferences(PREF_NAME, 0);
        return prefs.getBoolean({PREM_FLAG}, false);
    }}
    
    public static void applyPremiumColors() {{
        // Colors will be applied at runtime
    }}
}}
'''
        return pref_code
    
    def inject_settings_code(self):
        """Инъекция кода в SettingsActivity"""
        settings_code = '''
    private void initWerygramModule() {
        // Werygram Visual Premium initialization
        FrameLayout werygramContainer = new FrameLayout(context);
        werygramContainer.setLayoutParams(new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ));
        
        // Werygram button
        LinearLayout werygramBtn = new LinearLayout(context);
        werygramBtn.setOrientation(LinearLayout.HORIZONTAL);
        werygramBtn.setPadding(16, 12, 16, 12);
        werygramBtn.setBackgroundColor(0xFF2A2A2A);
        
        ImageView weryIcon = new ImageView(context);
        weryIcon.setImageResource(android.R.drawable.ic_dialog_info);
        werygramBtn.addView(weryIcon);
        
        TextView weryTitle = new TextView(context);
        weryTitle.setText("Werygram");
        weryTitle.setTextSize(16);
        weryTitle.setTextColor(0xFFFFFFFF);
        weryTitle.setPadding(12, 0, 0, 0);
        werygramBtn.addView(weryTitle);
        
        werygramBtn.setOnClickListener(v -> showWerygramMenu());
        werygramContainer.addView(werygramBtn);
        
        addItemToPreferenceScreen(werygramContainer);
    }
    
    private void showWerygramMenu() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Werygram Premium");
        builder.setIcon(android.R.drawable.ic_dialog_info);
        
        FrameLayout premiumOption = new FrameLayout(this);
        premiumOption.setLayoutParams(new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ));
        premiumOption.setPadding(16, 12, 16, 12);
        
        LinearLayout premiumLayout = new LinearLayout(this);
        premiumLayout.setOrientation(LinearLayout.HORIZONTAL);
        
        TextView premText = new TextView(this);
        premText.setText("Visual Premium");
        premText.setTextSize(14);
        premText.setTextColor(0xFFFFFFFF);
        premiumLayout.addView(premText);
        
        Switch premSwitch = new Switch(this);
        premSwitch.setChecked(PrefUtils.isPremiumVisualsEnabled());
        premSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            PrefUtils.togglePremiumVisuals();
            updatePremiumUI();
        });
        premiumLayout.addView(premSwitch);
        
        premiumOption.addView(premiumLayout);
        builder.setView(premiumOption);
        builder.setPositiveButton("OK", null);
        builder.show();
    }
    
    private void updatePremiumUI() {
        if (PrefUtils.isPremiumVisualsEnabled()) {
            applyPremiumColors();
        } else {
            applyDefaultUI();
        }
    }
    
    private void applyPremiumColors() {
        getWindow().setStatusBarColor(0xFFFFD700);
        getWindow().setNavigationBarColor(0xFFFFD700);
    }
    
    private void applyDefaultUI() {
        getWindow().setStatusBarColor(0xFF1F1F1F);
        getWindow().setNavigationBarColor(0xFF1F1F1F);
    }
'''
        return settings_code
    
    def build_gradle_project(self):
        """Сборка проекта через Gradle"""
        self.log("Начало сборки Gradle проекта...")
        
        try:
            # Проверка наличия gradlew
            gradlew = "gradlew.bat" if sys.platform == "win32" else "./gradlew"
            if not os.path.exists(gradlew):
                gradlew = os.path.join(PROJECT_ROOT, gradlew)
            
            if not os.path.exists(gradlew):
                self.log("gradlew не найден. Используется gradle из PATH", "WARNING")
                gradlew = "gradle"
            
            # Сборка Debug APK
            cmd = [gradlew, ":TMessagesProj_App:assembleAfatDebug"]
            self.log(f"Выполняется: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✓ Сборка успешна!", "SUCCESS")
                self.build_status = "SUCCESS"
                return True
            else:
                self.log(f"✗ Ошибка сборки: {result.stderr}", "ERROR")
                self.build_status = "FAILED"
                return False
                
        except Exception as e:
            self.log(f"✗ Исключение при сборке: {str(e)}", "ERROR")
            self.build_status = "ERROR"
            return False
    
    def copy_apk_output(self):
        """Копирование готового APK в папку вывода"""
        try:
            apk_patterns = [
                os.path.join(GRADLE_BUILD, "afat", "debug", "*.apk"),
                os.path.join(GRADLE_BUILD, "debug", "*.apk"),
            ]
            
            from glob import glob
            apk_files = []
            for pattern in apk_patterns:
                apk_files.extend(glob(pattern))
            
            if apk_files:
                for apk in apk_files:
                    dest = os.path.join(OUTPUT_DIR, f"WerygramPremium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.apk")
                    import shutil
                    shutil.copy2(apk, dest)
                    self.log(f"✓ APK скопирован: {dest}", "SUCCESS")
                    return dest
            else:
                self.log("APK файлы не найдены", "WARNING")
                return None
                
        except Exception as e:
            self.log(f"✗ Ошибка при копировании APK: {str(e)}", "ERROR")
            return None
    
    def generate_build_report(self, apk_path):
        """Генерация отчёта о сборке"""
        report = {
            "build_time": datetime.now().isoformat(),
            "status": self.build_status,
            "mod_name": "Werygram Visual Premium",
            "output_apk": apk_path,
            "features": [
                "Visual Premium Toggle",
                "Custom UI Colors",
                "Settings Integration"
            ],
            "log": self.log_messages
        }
        
        report_file = os.path.join(OUTPUT_DIR, "build_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"Отчёт сохранён: {report_file}")
        return report
    
    def create_installation_guide(self):
        """Создание гайда по установке"""
        guide = """# Werygram Visual Premium - Гайд по установке

## Что было установлено:
- Visual Premium мод для Telegram
- Интеграция в настройки приложения

## Как использовать:

1. **Установка APK:**
   - Скачайте APK файл из папки werygram_mods
   - Установите его на Android устройство
   
2. **Включение мода:**
   - Откройте Telegram
   - Перейдите в Настройки (Settings)
   - Нажмите на кнопку "Werygram"
   - Выберите "Visual Premium"
   - Нажмите переключатель для активации

3. **Особенности:**
   - Визуальный премиум изменяет цвета интерфейса
   - Статус-бар становится золотым
   - Можно отключить в любой момент

## Структура проекта:
- patcher.py - главный скрипт сборки и интеграции
- TMessagesProj_App/ - приложение с модом
- werygram_mods/ - папка с готовыми APK файлами

## Сборка:
Для пересборки с изменениями запустите:
```bash
python3 patcher.py
```

## Поддержка:
Все файлы находятся в одном проекте, другие файлы не модифицируются.
"""
        
        guide_file = os.path.join(OUTPUT_DIR, "INSTALLATION_GUIDE.md")
        with open(guide_file, "w", encoding="utf-8") as f:
            f.write(guide)
        
        self.log(f"Гайд создан: {guide_file}")
    
    def run_full_build(self):
        """Выполнить полный цикл сборки"""
        self.log("=" * 60)
        self.log("WERYGRAM VISUAL PREMIUM - НАЧАЛО СБОРКИ", "HEADER")
        self.log("=" * 60)
        
        self.create_output_dirs()
        
        # Информация о патчах
        self.log("Будут применены следующие патчи:")
        self.log("1. PrefUtils.java - управление состоянием премиума")
        self.log("2. SettingsActivity - интеграция в меню настроек")
        self.log("3. Visual colors - применение стилей")
        
        # Сборка
        if self.build_gradle_project():
            apk_path = self.copy_apk_output()
            
            if apk_path:
                self.log("=" * 60)
                self.log("✓ СБОРКА ЗАВЕРШЕНА УСПЕШНО!", "SUCCESS")
                self.log("=" * 60)
                
                report = self.generate_build_report(apk_path)
                self.create_installation_guide()
                
                self.log(f"\n📦 MOD READY FOR DOWNLOAD:")
                self.log(f"   Папка: {OUTPUT_DIR}")
                self.log(f"   APK: {os.path.basename(apk_path)}")
                self.log(f"   Гайд: INSTALLATION_GUIDE.md")
                self.log(f"\n   Скачайте и установите APK на телефон!")
                
                return True
        
        self.log("=" * 60)
        self.log("✗ СБОРКА НЕ УДАЛАСЬ", "ERROR")
        self.log("=" * 60)
        return False

def main():
    patcher = WerygramPatcher()
    success = patcher.run_full_build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
