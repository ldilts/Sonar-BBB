/*
    C ECHO client example using sockets
    https://github.com/luigif/hcsr04
*/
#include <stdio.h> //printf
#include <string.h>    //strlen
#include <sys/socket.h>    //socket
#include <arpa/inet.h> //inet_addr
#include <unistd.h>

#include <prussdrv.h>
#include <pruss_intc_mapping.h>
#include <stdbool.h>
 
int main(int argc , char *argv[])
{
    int sock;
    struct sockaddr_in server;
    char message[1000] , server_reply[2000];

    printf("Entrou Programa");     
    //Create socket
    sock = socket(AF_INET , SOCK_STREAM , 0);
    if (sock == -1)
    {
        printf("Could not create socket");
    }
    puts("Socket created");
     
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    server.sin_family = AF_INET;
    server.sin_port = htons( 10500 );
 
    //Connect to remote server
    if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
    {
        perror("connect failed. Error");
        return 1;
    }
     
    puts("Connected\n");

    /* Initialize the PRU */
    printf(">> Initializing PRU\n");
    tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
    prussdrv_init();

    /* Open PRU Interrupt */
    if (prussdrv_open (PRU_EVTOUT_0)) {
        // Handle failure
        fprintf(stderr, ">> PRU open failed\n");
        return 1;
    }

    /* Get the interrupt initialized */
    prussdrv_pruintc_init(&pruss_intc_initdata);

    /* Get pointers to PRU local memory */
    void *pruDataMem;
    prussdrv_map_prumem(PRUSS0_PRU0_DATARAM, &pruDataMem);
    unsigned int *pruData = (unsigned int *) pruDataMem;

    /* Execute code on PRU */
    printf(">> Executing HCSR-04 code\n");
    prussdrv_exec_program(0, "hcsr04.bin");
     
    //keep communicating with server
    int i = 0;
    while(1)
    {
	i++;
        // Wait for the PRU interrupt
        prussdrv_pru_wait_event (PRU_EVTOUT_0);
        prussdrv_pru_clear_event(PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);
        
        // Print the distance received from the sonar
        // At 20 degrees in dry air the speed of sound is 342.2 cm/sec
        // so it takes 29.12 us to make 1 cm, i.e. 58.44 us for a roundtrip of 1 cm
        printf("%3d: Distance = %.2f cm\n", i, (float) pruData[0] / 58.44);

        float distance = (float) pruData[0] / 58.44;
        
        // printf("Enter message : ");
        // scanf("%s" , message);

	sprintf(message, %f, distance);
         
        //Send some data
        if( send(sock , message , strlen(message) , 0) < 0)
        {
            puts("Send failed");
            return 1;
        }
         
        //Receive a reply from the server
        if( recv(sock , server_reply , 2000 , 0) < 0)
        {
            puts("recv failed");
            break;
        }
         
        puts("Server reply :");
        puts(server_reply);

        sleep(1);
    }

    /* Disable PRU and close memory mapping*/
    prussdrv_pru_disable(0);
    prussdrv_exit();
    printf(">> PRU Disabled.\r\n");
     
    close(sock);
    return 0;
}
