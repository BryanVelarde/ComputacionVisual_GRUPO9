
#include <stdlib.h>
#include <GL/glut.h>

/****************
Codigo del Cono 
****************/
#include <math.h>

float dameX(float R, int N, int n);
float dameZ(float R, int N, int n);
void anillo(float R, float y, int N);
float fConoInvertido(float y);
void conoInvertidoAlambre(int N);
void formaAlambre(float H, int N, float(*f)(float y));
void ReduceToUnit(float vector[3]);
void RenderShaft(void);

//#define M_PI 3.141516

/*--------------------------------------------------------------------------
Devuelve el valor de x del punto que gira.
R: el radio de giro.
N: el número total de tramos en el anillo.
n: el tramo actual.
--------------------------------------------------------------------------*/
float dameX(float R, int N, int n) 
{
	float x = (float) R * cos(n * (2 * M_PI) / N);
	return x;
}

/*--------------------------------------------------------------------------
Devuelve el valor de z del punto que gira.
R: el radio de giro.
N: el número total de tramos en el anillo.
n: el tramo actual.
--------------------------------------------------------------------------*/
float dameZ(float R, int N, int n) 
{
	float z = (float) R * sin(n * (2 * M_PI) / N);
	return z;
}

/*--------------------------------------------------------------------------
Dibuja un anillo.
R: el radio del anillo.
y: la altura a la que se dibuja el anillo.
N: el número de tramos del anillo.
--------------------------------------------------------------------------*/
void anillo(float R, float y, int N) 
{
	int i;
	float x, z;
	
	glBegin(GL_LINE_LOOP);
	for(i = 0; i < N; i++) 
	{
		x = dameX(R, N, i);
		z = dameZ(R, N, i);
		glVertex3f(x, y, z);
	}
	glEnd();
}

/*--------------------------------------------------------------------------
Devuelve un valor de radio en función de la altura
que se le pasa como parámetro para dibujar un cono.
y: el valor de la altura.
--------------------------------------------------------------------------*/
float fCono(float y) 
{
	float alturaTotal = 100.0;
	return (alturaTotal / 2 - y) * (50.0 / (alturaTotal / 2));
}

/*--------------------------------------------------------------------------
Dibuja un cono.
N: el número de anillos y tramos en cada anillo
--------------------------------------------------------------------------*/
void conoAlambre(int N) 
{
	formaAlambre(100.0f, N, fCono);
}

/*--------------------------------------------------------------------------
Algoritmo de dibujo para una figura de revolución.
H: la altura de la figura.
N: el número de anillos y divisiones en cada anillo.
f(float y): puntero a la función que nos devuelve.
el valor de radio en función de y.
--------------------------------------------------------------------------*/
void formaAlambre(float H, int N, float(*f)(float y)) 
{
	int i;
	float y, r;    
	for(i = 0; i < N; i++) 
	{ 
		y = i * H / N - (H / 2);    // Para cada nivel de altura
		r = f(y);           // obtenemos el radio
		anillo(r, y, N);    // y dibujamos un anillo
	}
}


void ReduceToUnit(float vector[3])
{
	float length;

	length = (float)sqrt((vector[0]*vector[0]) + (vector[1]*vector[1]) + (vector[2]*vector[2]));
	
	if(length == 0.0f)
		length = 1.0f;
	
	vector[0] /= length;
	vector[1] /= length;
	vector[2] /= length;
}


void Key (unsigned char tecla, int x, int y) 
{
	switch (tecla)
	{
	case 27 :
		exit (0);
		break;
	}
}

/*--------------------------------------------------------------------------
Borra la ventana y establece el color de dibujo y el ancho de las lineas
--------------------------------------------------------------------------*/
void display(void) 
{
	glClearColor (1.0,1.0,1.0, 1.0);
	glClear (GL_COLOR_BUFFER_BIT);
	glColor3f(1.0f, 0.0f, 0.0f);
	glLoadIdentity ();
	glPushMatrix();
	glTranslatef(0.0f, 0.0f, -4.0f);
	glRotatef(15.0f, 1.0f, 0.0f, 0.0f);    
	conoAlambre(20);
	//RenderShaft();
	
	glPopMatrix();
	glFlush ();
}

/*--------------------------------------------------------------------------
Esta función se llama al cambiar el tamaño de la ventana.
width, height: ancho y alto de la zona de dibujo.
--------------------------------------------------------------------------*/
void reshape(int width, int height) 
{
	glViewport (0, 0, width, height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	glOrtho(-100.0f, 100.0f, -100.0f, 100.0f, -100.0f, 100.0f);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
}

/*--------------------------------------------------------------------------
Función main.
argc: número de argumentos pasados al iniciar el programa.
**argv: array con cada uno de los argumentos.
--------------------------------------------------------------------------*/
int main (int argc, char** argv) 
{
	glutInit(&argc, argv);
	glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB);
	glutInitWindowSize (700, 700);
	glutInitWindowPosition (200, 30);
	glutCreateWindow (argv[0]);
	glutDisplayFunc (display);
	glutReshapeFunc (reshape);
	glutKeyboardFunc(Key); // Añadido para manejar las teclas
	glutMainLoop();
	return (1);
}
