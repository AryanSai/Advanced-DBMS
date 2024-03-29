#include <iostream>
#include <unordered_map>
#include <list>

using namespace std;

enum LockType {
    SHARED,
    EXCLUSIVE
};

enum LockStatus {
    GRANTED,
    WAITING
};

class LockableResource {
private:
    uint32_t txn_id_;
    LockType lock_type_;
    LockStatus lock_status_;

public:
    LockableResource(uint32_t txn_id, LockType lock_type, LockStatus lock_status) :
        txn_id_(txn_id), lock_type_(lock_type), lock_status_(lock_status) {}

    uint32_t getTxnId() const {
        return txn_id_;
    }

    LockType getLockType() const {
        return lock_type_;
    }

    LockStatus getLockStatus() const {
        return lock_status_;
    }

    void setLockStatus(LockStatus status) {
        lock_status_ = status;
    }
};

unordered_map<string, list<LockableResource*>> lock_table;

bool checkCompatibility(const string& resource_name, LockType lock_type) {
    if (lock_table.find(resource_name) != lock_table.end()) {
        list<LockableResource*>& resource_list = lock_table[resource_name];
        for (LockableResource* resource : resource_list) {
            if (resource->getLockType() == EXCLUSIVE || lock_type == EXCLUSIVE) {
                // Exclusive lock or existing exclusive lock present, not compatible
                return false;
            }
        }
    }
    return true;
}

bool lock(const string& resource_name, uint32_t txn_id, LockType lock_type) {
    if (lock_table.find(resource_name) == lock_table.end()) {
        lock_table[resource_name] = list<LockableResource*>();
    }

    if (checkCompatibility(resource_name, lock_type)) {
        LockableResource* new_resource = new LockableResource(txn_id, lock_type, GRANTED);
        lock_table[resource_name].push_back(new_resource);
        return true;
    }

    return false;
}

bool unlock(const string& resource_name, uint32_t txn_id) {
    if (lock_table.find(resource_name) != lock_table.end()) {
        list<LockableResource*>& resource_list = lock_table[resource_name];
        for (auto it = resource_list.begin(); it != resource_list.end(); ++it) {
            if ((*it)->getTxnId() == txn_id) {
                delete *it;
                resource_list.erase(it);
                return true;
            }
        }
    }
    return false;
}

int main() {
    bool ret = lock("AAA", 1234, EXCLUSIVE);
    if (ret) {
        cout << "Resource AAA locked in EXCLUSIVE mode for transaction 1234.\n";
    } else {
        cout << "Failed to lock resource AAA for transaction 1234.\n";
    }

    ret = lock("AAA", 4567, EXCLUSIVE);
    if (ret) {
        cout << "Resource AAA locked in EXCLUSIVE mode for transaction 4567.\n";
    } else {
        cout << "Failed to lock resource AAA for transaction 4567.\n";
    }

    ret = lock("BBB", 7890, SHARED);
    if (ret) {
        cout << "Resource BBB locked in SHARED mode for transaction 7890.\n";
    } else {
        cout << "Failed to lock resource BBB for transaction 7890.\n";
    }

    ret = unlock("AAA", 1234);
    if (ret) {
        cout << "Resource AAA unlocked for transaction 1234.\n";
    } else {
        cout << "Failed to unlock resource AAA for transaction 1234.\n";
    }

    return 0;
}
