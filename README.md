Team number: xohw22-107

Project name: Computer vision application featuring neural networks on Zybo-Z7 using the Vitis Unified Software Platform

Link to YouTube Video(s):

Link to project repository: [https://github.com/alex2kameboss/xohw22-107](https://github.com/alex2kameboss/xohw22-107)

 

University name: Transilvania University from Brasov, Romania

Participant(s): George Feldioreanu, Alexandru Pușcașu, Raul Milchiș

Email:

<copy above if necessary for each participant>

Supervisor name: Catalin Ciobanu

Supervisor e-mail:

 

Board used: Pynq Z2

Software Version:

* Vivado 2021.2
* Petalinux 2021.2
* Vitis AI 2.0
* VART 2.0

Brief description of project:

 

Description of archive (explain directory structure, documents and source files):

* In *files* folder are located all related file to build base platfrom
* *files/Vivado_2021_2* has the script to generate de hardware platform, required in petalainux
* *files/Petalinux_2021_2* has the petalinux project, compiled VART 2.0 for PYNQ Z2 and kernel lib for DPU 3.8
* In *dpu_test* are located testing scripts and and aditional resources
 

Instructions to build and test project:

* open Vivado 2021.2
* source *<repo_path>*/files/Vivado_2021_2/pynq_z2_dpu3.4_2021_2_hw.tcl
* start synthesis and generate bistream
* export project hardware
* create Petalinux 2021.2 project: petalinux-create -t project -s *<repo_path>*/files/Petalinux_2021_2/pynq_z2_dpu_2021_2_petalinux.bsp
* cd to petalinux project directory
* petalinux-config --get-hw-description *<path_to_eported_hardware>*
* petalinux-build
* petalinux-package --boot --u-boot --fpga
* follow [this steps](https://docs.xilinx.com/r/2021.2-English/ug1144-petalinux-tools-reference-guide/Steps-to-Boot-a-PetaLinux-Image-on-Hardware-with-SD-Card) to create a bootable SD card
* cp *<repo_path>*/files/Petalinux_2021_2/dpu.xclbin to BOOT partition
* extract *<repo_path>*/files/Petalinux_2021_2/vart2_pynq_z2.tar.gz to rootfs partiton
* cp directory *<repo_path>*/dpu_test to rootfs partition, recomanded home/petalinux
* etract in place *<rootfs>*/dpu_test/images
* plug SD card and power on
* connect to a serial monitor
* cd in dpu_test directory
* python3 fps_acc.py