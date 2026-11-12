// 同軸リレー制御 (12V ON/OFF) - RP2040-Zero / ESP32 共通スケッチ
//   RP2040-Zero : Arduino-Pico (Earle Philhower) コア
//   ESP32       : Arduino-ESP32 コア
//
// シリアルコマンド (行末 \n、大文字小文字は区別しない)
//   ON   : リレー通電 (ANT2)
//   OFF  : リレー非通電 (ANT1)
//   ?    : 状態問い合わせ
// 応答 : "STATE ON VIN 12.34 UP 120" / "STATE OFF VIN 12.34 UP 120"
//        UP は起動からの秒数（リセット検出用）。起動時に "BOOT" を送る
// RP2040はUSBを本体で扱うため、リセットするとUSB接続も一度切れる

#if defined(ARDUINO_ARCH_RP2040)
const int PIN_RELAY = 2;    // GP2  -> 2SC1815 ベース抵抗
const int PIN_VMON  = 26;   // GP26 (ADC0) <- 12V分圧
#elif defined(ARDUINO_ARCH_ESP32)
const int PIN_RELAY = 25;   // GPIO25 (ストラップピンではない)
const int PIN_VMON  = 32;   // GPIO32 (ADC1_CH4)
#else
#error "RP2040 か ESP32 を選択してください"
#endif

// 分圧比 (上側47k / 下側10k)。実測で合わない場合は VCAL で補正
const float DIV_RATIO = (47.0f + 10.0f) / 10.0f;
const float VCAL = 1.025f;   // 実測 12.12V ÷ 表示 11.83V (2026-11-12 校正)

bool relayOn = false;
String rx;

void setRelay(bool on) {
  relayOn = on;
  digitalWrite(PIN_RELAY, on ? HIGH : LOW);
}

float readVin() {
  uint32_t sum = 0;
  for (int i = 0; i < 16; i++) {
#if defined(ARDUINO_ARCH_ESP32)
    sum += analogReadMilliVolts(PIN_VMON);
#else
    sum += (uint32_t)analogRead(PIN_VMON) * 3300UL / 4095UL;
#endif
  }
  return (sum / 16.0f) / 1000.0f * DIV_RATIO * VCAL;
}

// 1行をまとめて送る（UP = 起動からの秒数。操作ページがリセットを検出するのに使う）
void report() {
  String s = "STATE ";
  s += relayOn ? "ON" : "OFF";
  s += " VIN ";
  s += String(readVin(), 2);
  s += " UP ";
  s += String(millis() / 1000UL);
  Serial.println(s);
}

void handle(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd.length() == 0) return;
  if (cmd == "ON")       { setRelay(true);  report(); }
  else if (cmd == "OFF") { setRelay(false); report(); }
  else if (cmd == "?")   { report(); }
  else { Serial.print("ERR "); Serial.println(cmd); }
}

void setup() {
  pinMode(PIN_RELAY, OUTPUT);
  setRelay(false);              // 起動時は必ず非通電 (ANT1)
#if defined(ARDUINO_ARCH_RP2040)
  analogReadResolution(12);
#else
  analogSetPinAttenuation(PIN_VMON, ADC_11db);
#endif
  Serial.begin(115200);
  delay(200);
  Serial.println("BOOT");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { handle(rx); rx = ""; }
    else if (c >= 0x20 && c < 0x7F && rx.length() < 32) rx += c;   // 制御文字（Ctrl+C等）は無視
  }
}
