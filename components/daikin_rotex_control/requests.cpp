#include "esphome/components/daikin_rotex_control/requests.h"
#include "esphome/core/hal.h"

namespace esphome {
namespace dakin_rotex_control {

TRequests::TRequests(IPublisher* pPublisher, std::vector<esphome::dakin_rotex_control::TRequest> const& requests)
: m_requests(requests)
, m_pCanBus(nullptr)
{
    for (auto& request : m_requests) {
        request.setPublisher(pPublisher);
    }
}

void TRequests::handle(uint32_t can_id, std::vector<uint8_t> const& responseData, uint32_t timestamp) {
    bool bHandled = false;
    for (auto& request : m_requests) {
        if (request.isMatch(can_id, responseData)) {
            request.handle(can_id, responseData, timestamp);
            bHandled = true;
        }
    }
    if (!bHandled) {
        Utils::log("request.h", "unhandled: can_id<%s> data<%s>", Utils::to_hex(can_id).c_str(), Utils::to_hex(responseData).c_str());
    }
}

bool TRequests::sendNextPendingGet() {
    TRequest* pRequest = getNextRequestToSend();
    if (pRequest != nullptr) {
        Utils::log("request.h", "sendNextPendingGet() -> found", "");
        pRequest->sendGet(m_pCanBus);
        return true;
    }
    return false;
}

void TRequests::sendGet(std::string const& request_name) {
    const auto it = std::find_if(m_requests.begin(), m_requests.end(),
        [& request_name](auto& request) { return request.getName() == request_name; });

    if (it != m_requests.end()) {
        it->sendGet(m_pCanBus);
    } else {
        Utils::log("request.h", "sendGet(%s) -> Unknown request!", request_name.c_str());
    }
}

void TRequests::sendSet(std::string const& request_name, float value) {
    const auto it = std::find_if(m_requests.begin(), m_requests.end(),
        [& request_name](auto& request) { return request.getName() == request_name; });

    if (it != m_requests.end()) {
        it->sendSet(m_pCanBus, value);
    } else {
        Utils::log("request.h", "sendSet(%s) -> Unknown request!", request_name.c_str());
    }
}

TRequest* TRequests::getNextRequestToSend() {
    const uint32_t timestamp = millis();
    const uint32_t interval = static_cast<uint32_t>(50/*id(update_interval).state*/) * 1000;

    //Utils::log("request.h", "getNextRequestToSend() -> timestamp: %d", timestamp);

    for (auto& request : m_requests) {
        if (request.hasSendGet()) {
            //Utils::log("request.h", "getNextRequestToSend() -> timestamp: %d, lu: %d, interval: %d, prog: %d", 
            //    timestamp, request.getLastUpdate(), interval, request.inProgress());

            if ((timestamp > (request.getLastUpdate() + interval)) && !request.inProgress()) {
                return &request;
            }
        }
    }
    return nullptr;
}

}
}