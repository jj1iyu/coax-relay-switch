// 同軸リレー制御 (12V ON/OFF) - RP2040-Zero / ESP32 共通スケッチ
//   RP2040-Zero : Arduino-Pico (Earle Philhower) コア / ボード "Waveshare RP2040 Zero"
//   ESP32       : Arduino-ESP32 コア
//
// シリアルコマンド (115200bps, 行末 \n、大文字小文字は区別しない)
//   ON          : 出力ON  (ANT B)
//   OFF         : 出力OFF (ANT A)
//   ?           : 状態問い合わせ        -> "STATE ON VIN 12.10 UP 120"
//   VER         : 版と校正値            -> "VER 0.3.0 CAL 1.0245"
//   CAL 12.12   : テスターで測った12Vの実測値を渡して校正（校正値はフラッシュに保存）
//   CAL RESET   : 校正値を 1.0 に戻す
//   BOOTSEL     : 書き込みモード(RPI-RP2ドライブ)で再起動（RP2040のみ。BOOTボタン不要で更新できる）
// 起動時に "BOOT 0.3.0" を送る。UP は起動からの秒数（リセット検出用）
// RP2040はUSBを本体で扱うため、リセットするとUSB接続も一度切れる

#include <EEPROM.h>

#define FW_VERSION "0.3.0"   // ← 更新するたびに上げる（GitHub Actions がこの値を読んで版情報を公開する）

#if defined(ARDUINO_ARCH_RP2040)
const int PIN_RELAY = 2;    // GP2  -> R1 -> 2SC1815 -> IRFU9024N
const int PIN_VMON  = 26;   // GP26 (ADC0) <- 12V分圧
#elif defined(ARDUINO_ARCH_ESP32)
const int PIN_RELAY = 25;   // GPIO25 (ストラップピンではない)
const int PIN_VMON  = 32;   // GPIO32 (ADC1_CH4)
#else
#error "RP2040 か ESP32 を選択してください"
#endif

// 分圧比 (上側47k / 下側10k)
const float DIV_RATIO = (47.0f + 10.0f) / 10.0f;

// 校正値（フラッシュに保存）
const uint32_t CAL_MAGIC = 0xC0A5CA1Bu;
struct CalData { uint32_t magic; float vcal; };
float vcal = 1.0f;

bool relayOn = false;
String rx;

void setRelay(bool on) {
  relayOn = on;
  digitalWrite(PIN_RELAY, on ? HIGH : LOW);
}

void loadCal() {
  CalData d;
  EEPROM.get(0, d);
  if (d.magic == CAL_MAGIC && d.vcal > 0.8f && d.vcal < 1.2f) vcal = d.vcal;
  else vcal = 1.0f;
}

bool saveCal(float v) {
  CalData d = { CAL_MAGIC, v };
  EEPROM.put(0, d);
  bool ok = EEPROM.commit();
  if (ok) vcal = v;
  return ok;
}

// 校正前の電圧（分圧比だけを掛けた値）
float readVinRaw() {
  uint32_t sum = 0;
  for (int i = 0; i < 16; i++) {
#if defined(ARDUINO_ARCH_ESP32)
    sum += analogReadMilliVolts(PIN_VMON);
#else
    sum += (uint32_t)analogRead(PIN_VMON) * 3300UL / 4095UL;
#endif
  }
  return (sum / 16.0f) / 1000.0f * DIV_RATIO;
}

float readVin() { return readVinRaw() * vcal; }

// 1行をまとめて送る
void report() {
  String s = "STATE ";
  s += relayOn ? "ON" : "OFF";
  s += " VIN ";
  s += String(readVin(), 2);
  s += " UP ";
  s += String(millis() / 1000UL);
  Serial.println(s);
}

void reportVer() {
  String s = "VER " FW_VERSION " CAL ";
  s += String(vcal, 4);
  Serial.println(s);
}

void handle(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd.length() == 0) return;

  if (cmd == "ON")       { setRelay(true);  report(); }
  else if (cmd == "OFF") { setRelay(false); report(); }
  else if (cmd == "?")   { report(); }
  else if (cmd == "VER") { reportVer(); }
  else if (cmd == "CAL RESET") {
    if (saveCal(1.0f)) { Serial.println("CAL OK 1.0000"); reportVer(); }
    else Serial.println("ERR CAL SAVE");
  }
  else if (cmd.startsWith("CAL ")) {
    float measured = cmd.substring(4).toFloat();
    float raw = readVinRaw();
    if (measured < 5.0f || measured > 20.0f) { Serial.println("ERR CAL RANGE (5-20V)"); return; }
    if (raw < 3.0f)                         { Serial.println("ERR CAL NO 12V"); return; }
    float v = measured / raw;
    if (v < 0.8f || v > 1.2f)               { Serial.println("ERR CAL FACTOR"); return; }
    if (saveCal(v)) { Serial.print("CAL OK "); Serial.println(v, 4); report(); }
    else Serial.println("ERR CAL SAVE");
  }
  else if (cmd == "BOOTSEL") {
#if defined(ARDUINO_ARCH_RP2040)
    setRelay(false);                 // 念のため出力OFF（再起動中もR2/R7でOFFが保たれる）
    Serial.println("BOOTSEL");
    Serial.flush();
    delay(200);
    rp2040.rebootToBootloader();     // RPI-RP2 ドライブとして再起動
#else
    Serial.println("ERR BOOTSEL NOT SUPPORTED");
#endif
  }
  else { Serial.print("ERR "); Serial.println(cmd); }
}

void setup() {
  pinMode(PIN_RELAY, OUTPUT);
  setRelay(false);                   // 起動時は必ず非通電 (ANT A)
#if defined(ARDUINO_ARCH_RP2040)
  analogReadResolution(12);
#else
  analogSetPinAttenuation(PIN_VMON, ADC_11db);
#endif
  EEPROM.begin(64);
  loadCal();
  Serial.begin(115200);
  delay(200);
  Serial.println("BOOT " FW_VERSION);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { handle(rx); rx = ""; }
    else if (c >= 0x20 && c < 0x7F && rx.length() < 32) rx += c;   // 制御文字（Ctrl+C等）は無視
  }
}
