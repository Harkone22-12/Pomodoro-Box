#include "timer_flow.h"
#include "pins.h"
#include "topics.h"
#include "../net/net.h"

// TODO(hao): PIN_BUZZER as OUTPUT, set BUZZER_OFF, netSubscribe(TOPIC_TIMER, timerOnMessage).
void timerSetup() {
}

// TODO(hao): when the countdown ends, sound the buzzer (BUZZER_ON) for a short time without delay().
void timerLoop() {
}

// TODO(hao): parse {"minutes": number}, validate it, start the countdown.
void timerOnMessage(const char* payload, size_t length) {
}
