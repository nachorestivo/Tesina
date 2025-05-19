import mysql.connector

db_host= "localhost"
db_user= "root" 
db_password= "root"
db_name= "escuela"

try:
    conexion = mysql.connector.connect(
    host = db_host,
    user = db_user,
    password = db_password,
    database = db_name
)

    cursor = conexion.cursor()
    consulta = "select nombre from estudiantes where materia = %s"
    valor_materia = ('informatica',)

    cursor.execute(consulta,valor_materia)
    resultados = cursor.fetchall()

    print("estudiantes de la materia matematicas:")
    for estudiantes in resultados: 
        print(estudiantes[0])
        
from create_student import insert_student
from read_student import get_students_by_carrera
from update_student import update_carrera
from delete_student import delete_student_by_id, delete_student_by_name

def main():
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Insertar un nuevo estudiante")
        print("2. Consultar estudiantes por carrera")
        print("3. Cambiar carrera de un estudiante")
        print("4. Eliminar un estudiante")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre = input("Nombre del estudiante: ")
            carrera = input("Carrera del estudiante: ")
            insert_student(nombre, carrera)

        elif opcion == '2':
            carrera = input("Carrera para buscar: ")
            estudiantes = get_students_by_carrera(carrera)
            if estudiantes:
                for est in estudiantes:
                    print(f"ID: {est[0]} - Nombre: {est[1]}")
            else:
                print("❌ No se encontraron estudiantes en esa carrera.")

        elif opcion == '3':
            id_estudiante = input("ID del estudiante a actualizar: ")
            nueva_carrera = input("Nueva carrera: ")
            if update_carrera(id_estudiante, nueva_carrera):
                print("✅ Carrera actualizada correctamente.")
            else:
                print("❌ No se encontró el estudiante.")

        elif opcion == '4':
            criterio = input("¿Eliminar por [1] ID o [2] Nombre?: ")
            if criterio == '1':
                id_estudiante = input("Ingrese el ID: ")
                if delete_student_by_id(id_estudiante):
                    print("✅ Estudiante eliminado correctamente.")
                else:
                    print("❌ No se encontró el estudiante.")
            elif criterio == '2':
                nombre = input("Ingrese el nombre: ")
                if delete_student_by_name(nombre):
                    print("✅ Estudiante eliminado correctamente.")
                else:
                    print("❌ No se encontró el estudiante.")
            else:
                print("❌ Opción inválida.")

        elif opcion == '5':
            print("👋 Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida, intente de nuevo.")

if __name__ == "__main__":
    main()    
except mysql.connector.error as error:
    print("error al conectar mysql: {error}")
finally:
    if conexion.is_connected():
        cursor.close()
        conexion.close()
        print("conexion a mysql cerrada.")