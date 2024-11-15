# Linux SysAdmin File Permissions Cheat Sheet

This cheat sheet helps sysadmins quickly interpret and set Linux file permissions.  
Linux file permissions consist of three permission sets for three user types: **Owner**, **Group**, and **Others**. 
Each set has three permissions: **Read (r)**, **Write (w)**, and **Execute (x)**.

---

## Symbolic Notation
Permissions are represented as a string of 10 characters, e.g., `drwxr-xr--`:
- **1st character**: File type:
  - `-` for regular file  
  - `d` for directory  
  - `l` for link  
- **Next 9 characters**: Three sets of permissions for **Owner**, **Group**, and **Others**.
  - `r` = Read (4)
  - `w` = Write (2)
  - `x` = Execute (1)
  - `-` = No permission

**Example**: `-rw-r--r--`  
- **Owner**: `rw-` (Read, Write)  
- **Group**: `r--` (Read only)  
- **Others**: `r--` (Read only)

---

## Numerical Notation
Permissions can also be represented numerically:
- **4** = Read (`r`)
- **2** = Write (`w`)
- **1** = Execute (`x`)
- Each permission set is the sum of these values.

**Example**: `744`
- **Owner**: 7 (`rwx` - Read, Write, Execute)
- **Group**: 4 (`r--` - Read only)
- **Others**: 4 (`r--` - Read only)

---

## Common Permission Codes
- **777** – Full access for all  
- **755** – Owner full access; Group/Others can read/execute  
- **644** – Owner can read/write; Group/Others can read only  

---
