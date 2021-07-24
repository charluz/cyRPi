#include <wiringSerial.h>


void main(void)                                              
{                                                            
    int fdSerial;                                            
                                                             
    fdSerial = serialOpen("/dev/ttyUSB0", 115200);           
                                                             
    serialPrintf(fdSerial, "Hello World!\n");                
                                                              
    serialClose(fdSerial);                                   
}    
