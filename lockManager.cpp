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
// we are assuming that the txns are ordered acc to time of their arrival
bool unlock(string resource_name, uint32_t txn_id)
{
  // check if the resource_name is even there in the lock_table
  if (lock_table.find(resource_name) == lock_table.end())
  {
    cout << "Cannot unlock a non-existent lock!";
    return false;
  }
  // if it is there, then get its corresponding list
  list<lockable_resource *> *res_list = lock_table[resource_name];
  lockable_resource *res;
  // check if the required txn_id is in the res_list
  for (auto i = res_list->begin(); i != res_list->end(); i++)
  {
    res = *i;
    uint32_t res_txn_id = res->getTxnId();
    // once the txn_id is found, delete it from the list => unlock
    if (res_txn_id == txn_id)
    {
      res_list->erase(i);
      delete res;
      if (res_list->empty())
        lock_table.erase(resource_name);
      break;
    }
  }
  // if the first txn in the remaining list is exclusive, grant it
  // if the first txn in the remaining list is shared, grant all waiting shared
  res = *res_list->begin(); // the first in the list
  if (res->getLockType() == lockType::EXCLUSIVE && res->getStatus() == lockStatus::WAITING)
  {
    res->setLockStatus(lockStatus::GRANTED);
  }
  else
  {
    for (auto i = res_list->begin(); i != res_list->end(); i++)
    {
      res = *i;
      if (res->getLockType() == lockType::SHARED && res->getStatus() == lockStatus::WAITING)
      {
        res->setLockStatus(lockStatus::GRANTED);
      }
    }
  }
  return true;
}

bool lock(string resource_name, uint32_t txn_id, uint8_t lock_type)
{
  uint8_t lock_status = lockStatus::WAITING; // default is waiting
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
      // check if the requesting transaction already in the list, then unlock in the end
      list<lockable_resource *>::iterator i;
      int unlocked = 0;
      for (i = lock_table[resource_name]->begin(); i != lock_table[resource_name]->end(); i++)
      {
        if ((*i)->getTxnId() == txn_id)
        {
          unlocked = 1;
          break;
        }
      }

      // Lock can be GRANTED when
      //     => the requested lock is compatible with existing the locks
      //     => if earlier requests are all granted

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

        // if reached the end, that is all existing are shared and granted
        // no worries, grant this also
        if (i == lock_table[resource_name]->end())
          lock_status = lockStatus::GRANTED;
        // else WAITING, taken care below
      }

      // WAIT if EXCLUSIVE is requested
      // WAIT if a prior txn is still WAITING
      lockable_resource *lr = new lockable_resource(txn_id, lock_type, lock_status);
      lock_table[resource_name]->emplace_back(lr);

      // unlock the previous lock issued by the txn
      if (unlocked == 1)
        unlock(resource_name, txn_id);
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
  cout << "-------------------------------------------------------" << endl;
  if (lock_table.empty())
    cout << "Lock Table is empty." << endl;
  else
  {
    cout << "\n----------------------LOCK TABLE----------------------" << endl;
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
  }
  cout << "-------------------------------------------------------" << endl;
}

int main()
{
  int option;
  uint8_t lock_type;
  uint32_t txn_id;
  string resource_name;
  cout << "---------------------Lock Manager---------------------" << endl;

  while (1)
  {
    cout << "1. Lock" << endl;
    cout << "2. Unlock" << endl;
    cout << "3. Print Lock Table" << endl;
    cout << "4. Quit" << endl;
    cout << "Enter your option:";
    cin >> option;

    switch (option)
    {
    case 1:
      cout << "Name of the resource: ";
      cin >> resource_name;
      cout << "Transaction ID: ";
      // cin >> txn_id;
      while (!(cin >> txn_id)) // when a non-numeric values is entered
      {
        cout << "Invalid input. Please enter a valid transaction ID: ";
        cin.clear();                                         // clear error flags
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // discard invalid input
      }
      while (1)
      {
        cout << "Type of the Lock (S/X): ";
        cin >> lock_type;
        if (lock_type == 'S' || lock_type == 's')
        {
          lock_type = lockType::SHARED;
          break;
        }
        else if (lock_type == 'X' || lock_type == 'x')
        {
          lock_type = lockType::EXCLUSIVE;
          break;
        }
        else
          cout << "Enter a valid lock! (S/X)\n";
      }
      if (!lock(resource_name, txn_id, lock_type))
        cout << "Lock error!" << endl;
      else
        cout << "Lock Successful!" << endl;
      print_locktable();
      break;
    case 2:
      cout << "Name of the resource: ";
      cin >> resource_name;
      cout << "Transaction ID: ";
      cin >> txn_id;
      if (!unlock(resource_name, txn_id))
        cout << "Unlock error!" << endl;
      else
        cout << "Unlock Successful!" << endl;
      print_locktable();
      break;
    case 3:
      print_locktable();
      break;
    case 4:
      return 0;
    default:
      cout << "Please enter a valid option (1, 2, 3, or 4)!" << endl;
      cin.clear();                                         // clear error flags
      cin.ignore(numeric_limits<streamsize>::max(), '\n'); // discard invalid input
      cout << "-------------------------------------------------------" << endl;
      break;
    }
  }
  return 0;
}