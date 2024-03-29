/*
Written by:
    Aryan Sai Arvapelly, Reg. No. 23352

Goal : Build a lock manager.
The lock manager should support the following capabilities:
1. Lock a resource in either shared or exclusive mode.
2. Unlock a resource held by a transaction.
A resource will be identified by a 10 character string.
*/

#include <iostream>
#include <unordered_map>
#include <list>

using namespace std;

// Abstraction of a resource that can be locked.
// A resource is locked in a 'mode' by a 'transaction'.
// The lock request may be granted or put on wait based
// on a lock compatibility matrix.
class lockable_resource
{
private:
  uint32_t txn_id_;
  uint8_t lock_type_;   // SHARED, EXCLUSIVE
  uint8_t lock_status_; // GRANTED, WAITING
public:
  lockable_resource(
      uint32_t txn_id,
      uint8_t lock_type,
      uint8_t lock_status) : txn_id_(txn_id),
                             lock_type_(lock_type),
                             lock_status_(lock_status)
  {
  }
  uint8_t getLockType()
  {
    return (lock_type_);
  }
  uint8_t getStatus()
  {
    return (lock_status_);
  }
  uint8_t getTxnId()
  {
    return (txn_id_);
  }
  bool setLockStatus(uint8_t st)
  {
    lock_status_ = st;
    return true;
  }
};

enum lockType
{
  SHARED,
  EXCLUSIVE
};

enum lockStatus
{
  GRANTED,
  WAITING
};

// map the resources to the list of transactions granted, waiting, sharing or exclusive
unordered_map<string, list<lockable_resource *> *> lock_table;

// changed the return type to bool for ease
bool unlock(string resource_name, uint32_t txn_id)
{
  // check if the resource_name is even there in the lock_table
  if (lock_table.find(resource_name) != lock_table.end())
  {
    // if it is there, then get its corresponding list
    list<lockable_resource *> *res_list = lock_table[resource_name];
    // check if the required txn_id is in the res_list
    for (auto i = res_list->begin(); i != res_list->end(); i++)
    {
      lockable_resource *res = *i;
      uint32_t res_txn_id = res->getTxnId();
      cout << res_txn_id << endl;
      // once the txn_id is found, delete it from the list => unlock
      if (res_txn_id == txn_id)
      {
        res_list->erase(i);
        delete res;
        return true;
      }
    }
  }
  return false;
}

bool lock(string resource_name, uint32_t txn_id, uint8_t lock_type)
{
  try
  {
    // if resource not in the lock_table, add it to the table
    if (lock_table.find(resource_name) == lock_table.end())
    {
      lockable_resource *lr = new lockable_resource(txn_id, lock_type, lockStatus::GRANTED);
      list<lockable_resource *> *lst = new list<lockable_resource *>;
      lst->emplace_back(lr);
      lock_table[resource_name] = lst;
      return true;
    }
    else // the resource is in the lock_table
    {
      // check if the requesting transaction already in the list, then unlock and then change
      list<lockable_resource *>::iterator i;
      for (i = lock_table[resource_name]->begin(); i != lock_table[resource_name]->end(); i++)
      {
        if ((*i)->getTxnId() == txn_id)
        {
          unlock(resource_name, txn_id);
          break;
        }
      }

      // Lock can be GRANTED when
      //     => the requested lock is compatible with existing the locks
      //     => if earlier requests are all granted

      uint8_t lock_status;
      // when SHARED is requested
      if (lock_type == lockType::SHARED)
      {
        lockable_resource *record;
        // all existing ones are shared and granted
        for (i = lock_table[resource_name]->begin(), record = *i;
             i != lock_table[resource_name]->end() &&
             record->getLockType() == lockType::SHARED &&
             record->getStatus() == lockStatus::GRANTED;
             i++, record = *i)
          ;

        // reached the end, that is all existing are shared and granted
        // no worries, grant this also
        if (i == lock_table[resource_name]->end())
          lock_status = lockStatus::GRANTED;
      }

      // WAIT if EXCLUSIVE is requested
      lock_status = lockStatus::WAITING;
      lockable_resource *lr = new lockable_resource(txn_id, lock_type, lock_status);
      lock_table[resource_name]->emplace_back(lr);
    }
  } // catch memory allocation exceptions
  catch (bad_alloc &err)
  {
    cerr << "Memory Allocation Failed! " << err.what() << endl;
    return false;
  }
  return true; // there is nothing like lock returning false since in worst case it waits
}

void print_locktable()
{
  cout << "\n----------------LOCK TABLE----------------" << endl;
  for (auto &record : lock_table)
  {
    cout << "Resource Name: " << record.first << endl;
    cout << "Details:" << endl;
    for (auto &resource : *record.second)
    {
      cout << "Txn ID: " << static_cast<int>(resource->getTxnId());
      cout << "\t";
      if (resource->getLockType() == lockType::EXCLUSIVE)
        cout << "LockType: EXCLUSIVE";
      else
        cout << "LockType: SHARED";
      cout << "\t";
      if (resource->getStatus() == lockStatus::WAITING)
        cout << "Status: WAITING";
      else
        cout << "Status: GRANTED";
      cout << endl;
    }
    cout << endl;
  }
  cout << "------------------------------------------" << endl;
}

int main()
{
  uint8_t option, lock_type, yes;
  uint32_t txn_id;
  string resource_name;
  cout << "------------------Lock Manager------------------" << endl;
  while (1)
  {
    cout << "Enter your option:" << endl;
    cout << "1. Lock" << endl;
    cout << "2. Unlock" << endl;
    cin >> option;

    cout << "Name of the resource: ";
    cin >> resource_name;
    cout << "Transaction ID: ";
    cin >> txn_id;

    switch (option)
    {
    case 1:
      while (1)
      {
        cout << "Type of the Lock (S/X): ";
        cin >> lock_type;
        if (lock_type == 'S')
        {
          lock_type = lockType::SHARED;
          break;
        }
        else if (lock_type == 'X')
        {
          lock_type = lockType::EXCLUSIVE;
          break;
        }
        else
          cerr << "Enter a valid lock! (S/X)\n";
      }
      if (!lock(resource_name, txn_id, lock_type))
        cerr << "Lock error!" << endl;
      break;
    case 2:
      if (!unlock(resource_name, txn_id))
        cerr << "Unlock error!" << endl;
      break;
    }

    print_locktable();

    cout << "\nDo you want to continue? Yes(1) : " << endl;
    cin >> yes;
    if (yes != '1')
    {
      cerr << "Bye!!!" << endl;
      break;
    }
  }
  return 0;
}
