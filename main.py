
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re


# =====================================================
# CONFIGURACION DEL REGISTRO DE EVENTOS Y ERRORES
# =====================================================

logging.basicConfig(
    filename="eventos.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# =====================================================
# EXCEPCIONES PERSONALIZADAS
# =====================================================

class ErrorSistema(Exception):
    """Excepcion general del sistema."""
    pass


class DatosInvalidosError(ErrorSistema):
    """Se genera cuando los datos ingresados son incorrectos."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Se genera cuando un servicio no esta disponible."""
    pass


class ReservaInvalidaError(ErrorSistema):
    """Se genera cuando una reserva no puede realizarse."""
    pass


# =====================================================
# CLASE ABSTRACTA ENTIDAD
# =====================================================

class Entidad(ABC):

    def __init__(self, identificacion, nombre):
        self._identificacion = identificacion
        self._nombre = nombre
        self._fecha_creacion = datetime.now()

    @property
    def identificacion(self):
        return self._identificacion

    @property
    def nombre(self):
        return self._nombre

    @abstractmethod
    def describir(self):
        pass


# =====================================================
# CLASE CLIENTE
# =====================================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion, nombre)

        if not nombre or not nombre.strip():
            raise DatosInvalidosError("El nombre es obligatorio.")

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
            raise DatosInvalidosError("El correo electronico no es valido.")

        if not telefono.isdigit() or len(telefono) < 7:
            raise DatosInvalidosError("El telefono debe tener minimo 7 digitos.")

        self.__correo = correo
        self.__telefono = telefono

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def describir(self):
        return (
            f"Cliente: {self.nombre} | "
            f"Correo: {self.correo} | "
            f"Telefono: {self.telefono}"
        )


# =====================================================
# CLASE ABSTRACTA SERVICIO
# =====================================================

class Servicio(Entidad, ABC):

    def __init__(self, identificacion, nombre, precio_hora):
        super().__init__(identificacion, nombre)

        if not isinstance(precio_hora, (int, float)) or precio_hora <= 0:
            raise DatosInvalidosError("El precio debe ser mayor que cero.")

        self._precio_hora = precio_hora
        self._disponible = True

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise DatosInvalidosError("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = valor

    @property
    def precio_hora(self):
        return self._precio_hora

    def calcular_costo(self, duracion, descuento=0, impuesto=0):
        """Calcula el costo con parametros opcionales."""

        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duracion debe ser mayor que cero.")

        if not 0 <= descuento <= 100:
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        if not 0 <= impuesto <= 100:
            raise DatosInvalidosError("El impuesto debe estar entre 0 y 100.")

        subtotal = self.precio_hora * duracion
        subtotal -= subtotal * (descuento / 100)
        total = subtotal + subtotal * (impuesto / 100)

        return round(total, 2)

    @abstractmethod
    def validar_parametros(self):
        pass


# =====================================================
# SERVICIO 1: RESERVA DE SALAS
# =====================================================

class ReservaSala(Servicio):

    def __init__(self, identificacion, nombre, precio_hora, capacidad):
        super().__init__(identificacion, nombre, precio_hora)

        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatosInvalidosError("La capacidad debe ser mayor que cero.")

        self.capacidad = capacidad

    def validar_parametros(self):
        return self.capacidad > 0

    def describir(self):
        return (
            f"Sala: {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | "
            f"Precio por hora: ${self.precio_hora}"
        )


# =====================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# =====================================================

class AlquilerEquipo(Servicio):

    def __init__(self, identificacion, nombre, precio_hora, unidades):
        super().__init__(identificacion, nombre, precio_hora)

        if not isinstance(unidades, int) or unidades <= 0:
            raise DatosInvalidosError("Las unidades deben ser mayores que cero.")

        self.unidades = unidades

    def validar_parametros(self):
        return self.unidades > 0

    def describir(self):
        return (
            f"Equipo: {self.nombre} | "
            f"Unidades: {self.unidades} | "
            f"Precio por hora: ${self.precio_hora}"
        )


# =====================================================
# SERVICIO 3: ASESORIAS ESPECIALIZADAS
# =====================================================

class Asesoria(Servicio):

    def __init__(self, identificacion, nombre, precio_hora, especialidad):
        super().__init__(identificacion, nombre, precio_hora)

        if not especialidad or not especialidad.strip():
            raise DatosInvalidosError("La especialidad es obligatoria.")

        self.especialidad = especialidad

    def validar_parametros(self):
        return bool(self.especialidad.strip())

    def describir(self):
        return (
            f"Asesoria: {self.nombre} | "
            f"Especialidad: {self.especialidad} | "
            f"Precio por hora: ${self.precio_hora}"
        )


# =====================================================
# CLASE RESERVA
# =====================================================

class Reserva(Entidad):

    def __init__(self, identificacion, cliente, servicio, duracion):
        super().__init__(identificacion, "Reserva")

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El cliente no es valido.")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El servicio no es valido.")

        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no esta disponible.")

        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ReservaInvalidaError("La duracion debe ser mayor que cero.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaInvalidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio ya no esta disponible."
            )

        self.estado = "Confirmada"
        logging.info(f"Reserva {self.identificacion} confirmada.")

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaInvalidaError("La reserva ya esta cancelada.")

        self.estado = "Cancelada"
        logging.info(f"Reserva {self.identificacion} cancelada.")

    def procesar(self):
        try:
            self.confirmar()
            return self.calcular_total()

        except ErrorSistema as error:
            logging.error(f"Error al procesar reserva: {error}")
            raise ReservaInvalidaError(
                "No fue posible procesar la reserva."
            ) from error

    def calcular_total(self, descuento=0, impuesto=0):
        return self.servicio.calcular_costo(
            self.duracion, descuento, impuesto
        )

    def describir(self):
        return (
            f"Reserva: {self.identificacion} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duracion: {self.duracion} horas | "
            f"Estado: {self.estado}"
        )


# =====================================================
# CLASE PRINCIPAL DEL SISTEMA
# =====================================================

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

        # Servicios iniciales de la empresa.
        self.servicios.append(
            ReservaSala("S01", "Sala de reuniones", 25000, 10)
        )

        self.servicios.append(
            AlquilerEquipo("S02", "Computador portatil", 12000, 5)
        )

        self.servicios.append(
            Asesoria("S03", "Asesoria informatica", 40000, "Informatica")
        )

    def registrar_cliente(self, nombre, correo, telefono):
        identificacion = f"C{len(self.clientes) + 1:03d}"

        try:
            cliente = Cliente(
                identificacion, nombre, correo, telefono
            )

            self.clientes.append(cliente)

            logging.info(f"Cliente registrado: {nombre}")
            return cliente

        except DatosInvalidosError as error:
            logging.error(f"Error al registrar cliente: {error}")
            raise

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto no es un servicio valido.")

        if any(s.identificacion == servicio.identificacion
               for s in self.servicios):
            raise DatosInvalidosError("El servicio ya esta registrado.")

        self.servicios.append(servicio)
        logging.info(f"Servicio registrado: {servicio.nombre}")

    def crear_reserva(self, cliente_id, servicio_id, duracion):
        cliente = next(
            (c for c in self.clientes if c.identificacion == cliente_id),
            None
        )

        servicio = next(
            (s for s in self.servicios if s.identificacion == servicio_id),
            None
        )

        if cliente is None:
            raise ReservaInvalidaError("El cliente no existe.")

        if servicio is None:
            raise ReservaInvalidaError("El servicio no existe.")

        try:
            reserva_id = f"R{len(self.reservas) + 1:03d}"

            reserva = Reserva(
                reserva_id, cliente, servicio, duracion
            )

            self.reservas.append(reserva)

            logging.info(f"Reserva creada: {reserva_id}")
            return reserva

        except ErrorSistema as error:
            logging.error(f"Error creando reserva: {error}")
            raise

    def buscar_reserva(self, identificacion):
        reserva = next(
            (r for r in self.reservas
             if r.identificacion == identificacion),
            None
        )

        if reserva is None:
            raise ReservaInvalidaError("La reserva no existe.")

        return reserva

    def listar_clientes(self):
        if not self.clientes:
            print("No hay clientes registrados.")
            return

        for cliente in self.clientes:
            print(cliente.describir())

    def listar_servicios(self):
        for servicio in self.servicios:
            estado = "Disponible" if servicio.disponible else "No disponible"
            print(servicio.describir(), "| Estado:", estado)

    def listar_reservas(self):
        if not self.reservas:
            print("No hay reservas registradas.")
            return

        for reserva in self.reservas:
            print(reserva.describir())


# =====================================================
# DEMOSTRACION DE 10 OPERACIONES
# =====================================================

def ejecutar_pruebas():
    print("\n" + "=" * 55)
    print(" DEMOSTRACION DE OPERACIONES - SOFTWARE FJ")
    print("=" * 55)

    sistema = SistemaSoftwareFJ()

    # OPERACION 1: Registro correcto de cliente.
    print("\nOPERACION 1: Registro de cliente valido")

    cliente = sistema.registrar_cliente(
        "Carlos Ramirez",
        "carlos@gmail.com",
        "3001234567"
    )
    print(cliente.describir())

    # OPERACION 2: Registro incorrecto de cliente.
    print("\nOPERACION 2: Registro de cliente invalido")

    try:
        sistema.registrar_cliente(
            " ",
            "correo_incorrecto",
            "123"
        )
    except DatosInvalidosError as error:
        print("Error controlado:", error)

    # OPERACION 3: Registro de un servicio valido.
    print("\nOPERACION 3: Registro de servicio valido")

    nuevo_servicio = ReservaSala(
        "S04", "Sala de capacitacion", 30000, 20
    )
    sistema.registrar_servicio(nuevo_servicio)
    print("Servicio registrado correctamente.")

    # OPERACION 4: Creacion de servicio invalido.
    print("\nOPERACION 4: Creacion de servicio invalido")

    try:
        servicio_invalido = ReservaSala(
            "S05", "Sala incorrecta", -1000, 10
        )
        sistema.registrar_servicio(servicio_invalido)

    except DatosInvalidosError as error:
        print("Error controlado:", error)

    # OPERACION 5: Registro de otro cliente valido.
    print("\nOPERACION 5: Segundo cliente")

    cliente2 = sistema.registrar_cliente(
        "Laura Martinez",
        "laura@gmail.com",
        "3107654321"
    )
    print(cliente2.describir())

    # OPERACION 6: Creacion de reserva exitosa.
    print("\nOPERACION 6: Crear reserva")

    reserva = sistema.crear_reserva(
        cliente.identificacion,
        "S01",
        2
    )
    print(reserva.describir())

    # OPERACION 7: Confirmacion de reserva.
    print("\nOPERACION 7: Confirmar reserva")

    reserva.confirmar()
    print("Estado:", reserva.estado)

    # OPERACION 8: Calculo de costo con descuento e impuesto.
    print("\nOPERACION 8: Calcular costo")

    total = reserva.calcular_total(descuento=10, impuesto=19)
    print(f"Costo total: ${total:,.2f}")

    # OPERACION 9: Intentar reservar un servicio no disponible.
    print("\nOPERACION 9: Reserva fallida")

    try:
        sistema.servicios[1].disponible = False

        sistema.crear_reserva(
            cliente2.identificacion,
            "S02",
            3
        )

    except ErrorSistema as error:
        print("Error controlado:", error)

    # OPERACION 10: Cancelar reserva.
    print("\nOPERACION 10: Cancelar reserva")

    reserva.cancelar()
    print("Estado:", reserva.estado)

    # Bloques else y finally.
    try:
        print("\nVerificacion final de las operaciones.")
    except Exception as error:
        logging.error(f"Error en verificacion: {error}")
    else:
        print("Verificacion ejecutada correctamente.")
    finally:
        print("Demostracion finalizada.")

    print("\n" + "=" * 55)
    print(" FIN DE LAS 10 OPERACIONES")
    print("=" * 55)

    return sistema


# =====================================================
# MENU PRINCIPAL
# =====================================================

def menu_principal():

    sistema = ejecutar_pruebas()

    while True:

        print("\n======================================")
        print("       SOFTWARE FJ")
        print(" SISTEMA DE GESTION DE RESERVAS")
        print("======================================")
        print("1. Registrar cliente")
        print("2. Mostrar clientes")
        print("3. Mostrar servicios")
        print("4. Crear reserva")
        print("5. Confirmar reserva")
        print("6. Cancelar reserva")
        print("7. Mostrar reservas")
        print("8. Salir")
        print("======================================")

        try:
            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":

                nombre = input("Nombre del cliente: ")
                correo = input("Correo electronico: ")
                telefono = input("Telefono: ")

                cliente = sistema.registrar_cliente(
                    nombre, correo, telefono
                )

                print("Cliente registrado:", cliente.identificacion)

            elif opcion == "2":
                sistema.listar_clientes()

            elif opcion == "3":
                sistema.listar_servicios()

            elif opcion == "4":

                cliente_id = input("ID del cliente: ").strip()
                servicio_id = input("ID del servicio: ").strip()
                duracion = float(input("Duracion en horas: "))

                reserva = sistema.crear_reserva(
                    cliente_id, servicio_id, duracion
                )

                print("Reserva creada:", reserva.identificacion)

            elif opcion == "5":

                reserva_id = input("ID de la reserva: ").strip()
                reserva = sistema.buscar_reserva(reserva_id)
                reserva.confirmar()

                print("Reserva confirmada.")

            elif opcion == "6":

                reserva_id = input("ID de la reserva: ").strip()
                reserva = sistema.buscar_reserva(reserva_id)
                reserva.cancelar()

                print("Reserva cancelada.")

            elif opcion == "7":
                sistema.listar_reservas()

            elif opcion == "8":
                print("Gracias por utilizar Software FJ.")
                break

            else:
                raise DatosInvalidosError(
                    "Seleccione una opcion del 1 al 8."
                )

        except ValueError:
            print("Error: debe ingresar un valor numerico valido.")
            logging.exception("Error de conversion de datos.")

        except ErrorSistema as error:
            print("Error controlado:", error)
            logging.exception("Error del sistema.")

        except Exception as error:
            print("Ocurrio un error inesperado:", error)
            logging.exception("Error inesperado.")

        else:
            print("Operacion ejecutada correctamente.")

        finally:
            print("\nFin de la operacion.")


# =====================================================
# EJECUCION DEL PROGRAMA
# =====================================================

if __name__ == "__main__":
    try:
        menu_principal()

    except Exception as error:
        logging.exception(f"Error general de ejecucion: {error}")
        print("El sistema encontro un error inesperado.")

