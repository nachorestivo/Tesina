-- =====================================================
-- Script SQL Unificado - Sistema de Turnos para Uñas
-- Base de datos: agendanails
-- =====================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- --------------------------------------------------------
-- Base de datos: `agendanails`
-- --------------------------------------------------------

-- Eliminar tablas si existen (para recrear desde cero)
DROP TABLE IF EXISTS `turnos`;
DROP TABLE IF EXISTS `servicios`;
DROP TABLE IF EXISTS `usuarios`;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `usuarios`
-- --------------------------------------------------------

CREATE TABLE `usuarios` (
  `id_Usuario` int(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_Usuario`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `servicios`
-- --------------------------------------------------------

CREATE TABLE `servicios` (
  `id_Servicios` int(11) NOT NULL AUTO_INCREMENT,
  `Tipo_de_servicio` varchar(100) NOT NULL,
  `Descripcion_del_servicio` text DEFAULT NULL,
  `Duracion` int(11) NOT NULL COMMENT 'Duración en minutos',
  `Precio` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_Servicios`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `turnos`
-- --------------------------------------------------------

CREATE TABLE `turnos` (
  `id_Turnos` int(11) NOT NULL AUTO_INCREMENT,
  `id_Usuario` int(20) NOT NULL COMMENT 'ID del usuario que agendó el turno',
  `id_Servicio` int(11) DEFAULT NULL COMMENT 'ID del servicio principal (opcional, puede haber múltiples)',
  `Servicios` text NOT NULL COMMENT 'Lista de servicios seleccionados (JSON o texto separado por comas)',
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `Total` decimal(10,2) NOT NULL,
  `Estado_del_turno` varchar(20) NOT NULL DEFAULT 'pendiente' COMMENT 'pendiente, confirmado, cancelado, completado',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_Turnos`),
  KEY `id_Usuario` (`id_Usuario`),
  KEY `id_Servicio` (`id_Servicio`),
  KEY `fecha` (`fecha`),
  KEY `Estado_del_turno` (`Estado_del_turno`),
  CONSTRAINT `turnos_ibfk_1` FOREIGN KEY (`id_Usuario`) REFERENCES `usuarios` (`id_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `turnos_ibfk_2` FOREIGN KEY (`id_Servicio`) REFERENCES `servicios` (`id_Servicios`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Datos de ejemplo para la tabla `servicios`
-- --------------------------------------------------------

INSERT INTO `servicios` (`Tipo_de_servicio`, `Descripcion_del_servicio`, `Duracion`, `Precio`) VALUES
('Esmaltado Semipermanente', 'Técnica que consiste en aplicar un gel o esmalte especial sobre la uña natural y secado con luz Led o UV. Deja un acabado brillante y duradero por 21 días.', 60, 10000.00),
('Soft Gel', 'El sistema de Soft Gel consiste en aplicar uñas de gel preformadas que se adhieren con gel y luz led, logrando extensiones duraderas y de aspecto natural.', 90, 18000.00),
('Capping', 'El capping consiste en proteger la uña natural aplicando una capa de gel o acrílico sobre ella sin alargarla. Aporta brillo, dureza y mayor duración al esmaltado.', 60, 15000.00),
('Sistema Polygel', 'El sistema Polygel combina acrílico y gel, logrando una textura resistente. Se usa para esculpir o alargar uñas, ofreciendo un acabado natural y duradero.', 120, 20000.00);

-- --------------------------------------------------------
-- Usuario administrador por defecto
-- Usuario: admin
-- Contraseña: admin123
-- --------------------------------------------------------

INSERT INTO `usuarios` (`username`, `email`, `password_hash`, `is_admin`, `created_at`) VALUES
('admin', 'admin@nailsstudio.com', 'scrypt:32768:8:1$hqND9owETOoAHj4S$2deda0f835f96255a288d3392c4f6e9da54d550bba664fbeb12f6292f4d907fae9cbc2bac1c1063875f52492ceab7acdb1397af8b49609be924bf277ab2e8395', 1, NOW());

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

