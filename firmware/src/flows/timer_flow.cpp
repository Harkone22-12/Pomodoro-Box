#include "timer_flow.h"
#include "pins.h"
#include "topics.h"
#include "../net/net.h"

// TODO(member3): PIN_BUZZER as OUTPUT, set BUZZER_OFF, netSubscribe(TOPIC_TIMER, timerOnMessage).
void timerSetup() {
}

// TODO(member3): when the countdown ends, sound the buzzer (BUZZER_ON) for a short time without delay().
void timerLoop() {
}

// TODO(member3): parse {"minutes": number}, validate it, start the countdown.
void timerOnMessage(const char* payload, size_t length) {
}
