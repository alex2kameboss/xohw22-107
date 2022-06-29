Team number: xohw22-107

Project name: Computer vision application featuring neural networks on Zybo-Z7 using the Vitis Unified Software Platform

Link to YouTube Video(s): https://www.youtube.com/watch?v=nvyxL31SzeY&ab_channel=RaulDaniel

Link to project repository: https://github.com/alex2kameboss/xohw22-107

 

University name: Transilvania University from Brasov, Romania

Participant(s): George Feldioreanu, Alexandru Pușcașu, Raul Milchiș

Email: george.feldioreanu@student.unitbv.ro , alexandru.puscasu@student.unitbv.ro , raul.milchis@student.unitbv.ro

Supervisor name: Catalin Ciobanu

Supervisor e-mail: catalin.ciobanu@unitbv.ro



Board used: Pynq Z2

Software Version:

* Vivado 2021.2
* Petalinux 2021.2
* Vitis AI 2.0
* VART 2.0

Brief description of project:

 

Description of archive (explain directory structure, documents and source files):

- files folder has all related file to build base platfrom
- files/Vivado_2021_2 folder has the script to generate the hardware platform, required in petalainux
- files/Petalinux_2021_2 folder has the petalinux project, compiled VART 2.0 for PYNQ Z2 and kernel lib for DPU 3.8
- dpu_test folder has testing scripts and aditional resources
- files/Vivado_2021_2/pynq_z2_dpu3.4_2021_2_hw.tcl - paltfrom bistream
- files/Vivado_2021_2/pynq_z2_dpu3.4_2021_2_hw.tcl - script for Vivado 2021.2 to build platform project
- files/Petalinux_2021_2/pynq_z2_dpu_2021_2_petalinux.bsp - bsp file for pynq z2 platform
- files/Petalinux_2021_2/dpu.xclbin - kernel lib for dpu
- files/Petalinux_2021_2/vart2_pynq_z2.tar.gz - compiled VART 2.0 for pynq z2

Instructions to build and test project:

Step 1. open Vivado 2021.2
Step 2. include DPU 3.8 into IP list - download Vitis AI repo and include to Vivado
Step 3. source <repo_path>/files/Vivado_2021_2/pynq_z2_dpu3.4_2021_2_hw.tcl
Step 4. start synthesis and generate bistream
Step 5. export project hardware
Step 6. create Petalinux 2021.2 project: petalinux-create -t project -s <repo_path>/files/Petalinux_2021_2/pynq_z2_dpu_2021_2_petalinux.bsp
Step 7. cd to petalinux project directory
Step 8. petalinux-config --get-hw-description <path_to_eported_hardware>
Step 9. petalinux-build
Step 10. petalinux-package --boot --u-boot --fpga
Step 11. follow this steps (https://docs.xilinx.com/r/2021.2-English/ug1144-petalinux-tools-reference-guide/Steps-to-Boot-a-PetaLinux-Image-on-Hardware-with-SD-Card) to create a bootable SD card
Step 12. cp <repo_path>/files/Petalinux_2021_2/dpu.xclbin to BOOT partition
Step 13. extract <repo_path>/files/Petalinux_2021_2/vart2_pynq_z2.tar.gz to rootfs partiton
Step 14. cp directory <repo_path>/dpu_test to rootfs partition, recomanded home/petalinux
Step 15. etract in place <rootfs>/dpu_test/images
Step 16. plug SD card and power on
Step 17. connect to a serial monitor (Recommanded speed 115200)
Step 18. cd in dpu_test directory
Step 19. python3 fps_acc.py
