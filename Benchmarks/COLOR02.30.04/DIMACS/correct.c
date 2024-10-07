#include<stdio.h>

main() 
{
  char ch;
  int i,j;
  
  while(scanf("%c",&ch)!= EOF) {
    if (ch == 'c') {
      while (ch != '\n') {
	printf("%c",ch);
	scanf("%c",&ch);
	
      }
      printf("\n");
    }
    else if (ch == 'p') {
      while (ch != '\n') {
	printf("%c",ch);
	scanf("%c",&ch);
      }
      printf("\n");
    }
    else if (ch = 'e') {
      scanf("%d %d",&i,&j);
      printf("e %d %d\n",i+1,j+1);
      scanf("%c",&ch);
      while (ch != '\n') {
	printf("%c",ch);
	scanf("%c",&ch);
      }
    
      
    }
    
  }
  
}


