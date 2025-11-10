-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 10-11-2025 a las 11:52:01
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `agendanails`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `servicios`
--

CREATE TABLE `servicios` (
  `id_Servicios` int(11) NOT NULL,
  `Tipo_de_servicio` varchar(100) NOT NULL,
  `Descripcion_del_servicio` text DEFAULT NULL,
  `Duracion` int(11) NOT NULL COMMENT 'Duración en minutos',
  `Precio` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `servicios`
--

INSERT INTO `servicios` (`id_Servicios`, `Tipo_de_servicio`, `Descripcion_del_servicio`, `Duracion`, `Precio`, `created_at`) VALUES
(1, 'Esmaltado Semipermanente', 'Técnica que consiste en aplicar un gel o esmalte especial sobre la uña natural y secado con luz Led o UV. Deja un acabado brillante y duradero por 21 días.', 60, 10000.00, '2025-11-07 17:12:01'),
(2, 'Soft Gel', 'El sistema de Soft Gel consiste en aplicar uñas de gel preformadas que se adhieren con gel y luz led, logrando extensiones duraderas y de aspecto natural.', 90, 18000.00, '2025-11-07 17:12:01'),
(3, 'Capping', 'El capping consiste en proteger la uña natural aplicando una capa de gel o acrílico sobre ella sin alargarla. Aporta brillo, dureza y mayor duración al esmaltado.', 60, 15000.00, '2025-11-07 17:12:01'),
(4, 'Sistema Polygel', 'El sistema Polygel combina acrílico y gel, logrando una textura resistente. Se usa para esculpir o alargar uñas, ofreciendo un acabado natural y duradero.', 120, 20000.00, '2025-11-07 17:12:01');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `turnos`
--

CREATE TABLE `turnos` (
  `id_Turnos` int(11) NOT NULL,
  `id_Usuario` int(20) NOT NULL COMMENT 'ID del usuario que agendó el turno',
  `id_Servicio` int(11) DEFAULT NULL COMMENT 'ID del servicio principal (opcional, puede haber múltiples)',
  `Servicios` text NOT NULL COMMENT 'Lista de servicios seleccionados (JSON o texto separado por comas)',
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `Total` decimal(10,2) NOT NULL,
  `Estado_del_turno` varchar(20) NOT NULL DEFAULT 'pendiente' COMMENT 'pendiente, confirmado, cancelado, completado',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `turnos`
--

INSERT INTO `turnos` (`id_Turnos`, `id_Usuario`, `id_Servicio`, `Servicios`, `fecha`, `hora`, `Total`, `Estado_del_turno`, `created_at`) VALUES
(1, 2, 2, 'Soft Gel', '2025-11-10', '20:20:00', 18000.00, 'pendiente', '2025-11-07 17:21:08'),
(2, 2, 2, 'Soft Gel', '2025-11-10', '18:00:00', 18000.00, 'confirmado', '2025-11-07 17:30:31'),
(3, 2, 1, 'Esmaltado Semipermanente', '2025-11-08', '18:30:00', 10000.00, 'pendiente', '2025-11-07 17:30:55'),
(4, 3, 1, 'Esmaltado Semipermanente', '2025-11-20', '03:25:00', 10000.00, 'pendiente', '2025-11-07 18:10:38'),
(5, 3, 3, 'Capping', '2025-11-13', '10:30:00', 15000.00, 'confirmado', '2025-11-07 18:11:39');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_Usuario` int(20) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_Usuario`, `username`, `email`, `password_hash`, `is_admin`, `created_at`) VALUES
(1, 'admin', 'admin@nailsstudio.com', 'scrypt:32768:8:1$hqND9owETOoAHj4S$2deda0f835f96255a288d3392c4f6e9da54d550bba664fbeb12f6292f4d907fae9cbc2bac1c1063875f52492ceab7acdb1397af8b49609be924bf277ab2e8395', 1, '2025-11-07 17:12:02'),
(2, 'vivig', 'vag@gmail.com', 'scrypt:32768:8:1$7WQtNGBGnsKMW7i4$acfaf1e95841a70cae04a86f2182904bca2ddf44bf63d6d13dd93aa6f283db105cbfc6465ef9239e82d2c732b114360878ad31af29b43d3a7fd5164d9e6acaea', 0, '2025-11-07 17:19:46'),
(3, 'juli', 'juli@gmail.com', 'scrypt:32768:8:1$Pmqwzx10X8pdPc0c$c3341822f5bb6a1aa59f58ee42de4ccf69b7e01f2a9dccfd8fd0bd82a3b01be2e3dfd54a68df5d4c61c4ac74b6b18acd0b48c5542a2d6ed5e382fbb3bc65238c', 0, '2025-11-07 18:09:57');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `servicios`
--
ALTER TABLE `servicios`
  ADD PRIMARY KEY (`id_Servicios`);

--
-- Indices de la tabla `turnos`
--
ALTER TABLE `turnos`
  ADD PRIMARY KEY (`id_Turnos`),
  ADD KEY `id_Usuario` (`id_Usuario`),
  ADD KEY `id_Servicio` (`id_Servicio`),
  ADD KEY `fecha` (`fecha`),
  ADD KEY `Estado_del_turno` (`Estado_del_turno`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_Usuario`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `servicios`
--
ALTER TABLE `servicios`
  MODIFY `id_Servicios` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `turnos`
--
ALTER TABLE `turnos`
  MODIFY `id_Turnos` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_Usuario` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `turnos`
--
ALTER TABLE `turnos`
  ADD CONSTRAINT `turnos_ibfk_1` FOREIGN KEY (`id_Usuario`) REFERENCES `usuarios` (`id_Usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `turnos_ibfk_2` FOREIGN KEY (`id_Servicio`) REFERENCES `servicios` (`id_Servicios`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
