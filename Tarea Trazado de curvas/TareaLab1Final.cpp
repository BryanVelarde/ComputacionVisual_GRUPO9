#include <GL/glut.h> 
#include <stdio.h> 

int x1, y1, x2, y2;

void reshape(int width, int height) 
{ 
	glViewport(0, 0, width, height); 
	glMatrixMode(GL_PROJECTION); 
	glLoadIdentity(); 
	glOrtho(-100, 100, -100, 100, -100, 100); 
	glMatrixMode(GL_MODELVIEW); 
} 

void write_pixel(int x, int y)
{
	glBegin(GL_POINTS); 
	glVertex3f(x,y,0); 
	glEnd(); 
}

void line_modif(int x1, int y1, int x2, int y2)
{
	int dx = x2 - x1;
	int dy = y2 - y1;
	int difer;
	
	if (abs(dx) > abs(dy)) {
		difer = abs(dx);
	} else {
		difer = abs(dy);
	}
	
	float aumento_x = dx / (float)difer;
	float aumento_y = dy / (float)difer;
	float x = x1;
	float y = y1;
	
	for (int i = 0; i <= difer; i++) {
		write_pixel((int)x, (int)y);
		x += aumento_x;
		y += aumento_y;
	}
}

void puntosParb(int x, int y) {
	write_pixel(x, y);
	write_pixel(-x, y); // Simétrico respecto al eje y
}

void MidpointParabola(int a, int b) {
	int x = 0;
	int y = 0;
	int d = 1 - a; 
	puntosParb(x, y);
	
	while (x < a) {
		x++;
		if (d < 0) {
			d += 2 * x + 1;
		} else {
			y++;
			d += 2 * (x - y) + 1;
		}
		puntosParb(x, y);
	}
}

void display() 
{ 
	
	glClear(GL_COLOR_BUFFER_BIT); 
	glColor3f(0,0,0); 
	glLoadIdentity(); 
	line_modif(x1, y1, x2, y2);
	//MidpointParabola(x2, y2); // Dibujar la parábola
	glFlush(); 
} 

void init() 
{ 
	glClearColor(1,1,1,1); 
} 


int main(int argc, char **argv) 
{ 
	printf("Ingresar x1, y1, x2, y2 \n");
	scanf("%d %d %d %d", &x1, &y1, &x2, &y2);
	
	glutInit(&argc, argv); 
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB); 
	glutInitWindowPosition(50, 50); 
	glutInitWindowSize(500, 500); 
	glutCreateWindow("Hello OpenGL"); 
	init(); 
	glutDisplayFunc(display); 
	glutReshapeFunc(reshape); 
	glutMainLoop(); 
	return 0; 
} 
	
