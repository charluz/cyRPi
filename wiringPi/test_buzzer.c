#include <stdio.h>
#include <wiringPi.h>

int main (void)
{
  wiringPiSetup () ;
  
  // connect '-'pin to GND, '+'pin to GPIO#0
  pinMode (0, OUTPUT) ;
  
  for (;;)
  {
	  printf("GPIO 0 --> HIGH\n");
	  digitalWrite(0, HIGH);
	  delay(1000);
	  printf("GPIO 0 --> LOW\n");
	  digitalWrite(0, LOW);
	  delay(1000);  
  }
  return 0 ;
}

