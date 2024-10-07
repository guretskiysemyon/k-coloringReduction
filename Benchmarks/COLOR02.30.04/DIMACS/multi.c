#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#define MAX_RANDOM_VALUE  ((double)(0x7FFFFFFF))

main() 
{
  char ch;
  int i,j;
  char junk[10];
  int num_node,num_edge;
  

  printf("Max random: %f\n",MAX_RANDOM_VALUE);
  
  while(scanf("%c",&ch)!= EOF) {
    if (ch == 'c') {
      while (ch != '\n') {
	printf("%c",ch);
	scanf("%c",&ch);
	
      }
      printf("\n");
    }
    else if (ch == 'p') {
      scanf("%s",junk);
      scanf("%d %d",&num_node,&num_edge);
      printf("p edge %d %d\n",num_node,num_edge);
      while (ch != '\n') {
	scanf("%c",&ch);
	
      }

    }
    else if (ch == 'e') {
      while (ch != '\n') {
	printf("%c",ch);
	scanf("%c",&ch);
      }
      printf("\n");
      
    }
    
  }
  srand(num_node*num_edge);
  
  for (i=1;i<=num_node;i++)
    printf("n %d %d\n",i,(int) ((rand()*5.0/2147483648.000)+1.0));

  
  
  
}
