-- TRATAMIENTO CATEGORÍAS
INSERT INTO treatment_categories (id, name, description, active, created_at) VALUES
(1, 'Consulta', 'Consultas y revisiones generales', 1, '2024-01-01 08:00:00'),
(2, 'Limpieza', 'Procedimientos de limpieza dental', 1, '2024-01-01 08:00:00'),
(3, 'Ortodoncia', 'Tratamientos de ortodoncia', 1, '2024-01-01 08:00:00'),
(4, 'Cirugía', 'Procedimientos quirúrgicos', 1, '2024-01-01 08:00:00'),
(5, 'Estética', 'Tratamientos estéticos', 1, '2024-01-01 08:00:00'),
(6, 'Endodoncia', 'Tratamientos de conducto', 1, '2024-01-01 08:00:00'),
(7, 'Prótesis', 'Prótesis dentales', 1, '2024-01-01 08:00:00'),
(8, 'Periodoncia', 'Tratamientos de encías', 1, '2024-01-01 08:00:00'),
(9, 'Radiología', 'Servicios radiológicos', 1, '2024-01-01 08:00:00'),
(10, 'Odontopediatría', 'Tratamientos para niños', 1, '2024-01-01 08:00:00');

-- TRATAMIENTOS
INSERT INTO treatments (id, category_id, name, description, default_price, duration, active, created_at, updated_at) VALUES
(1, 1, 'Consulta inicial', 'Primera consulta y evaluación general', 50.00, 30, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(2, 1, 'Revisión periódica', 'Consulta de seguimiento', 35.00, 20, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(3, 2, 'Limpieza dental simple', 'Limpieza dental básica', 70.00, 45, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(4, 2, 'Limpieza dental profunda', 'Limpieza dental avanzada', 120.00, 60, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(5, 3, 'Instalación de brackets', 'Colocación inicial de brackets', 500.00, 90, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(6, 3, 'Ajuste mensual de brackets', 'Ajuste periódico de ortodoncia', 80.00, 30, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(7, 4, 'Extracción simple', 'Extracción dental simple', 100.00, 40, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(8, 4, 'Extracción quirúrgica', 'Extracción dental compleja', 250.00, 60, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(9, 5, 'Blanqueamiento dental', 'Tratamiento de blanqueamiento completo', 300.00, 60, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(10, 5, 'Carilla dental', 'Aplicación de carilla por pieza', 350.00, 75, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(11, 6, 'Endodoncia uniradicular', 'Tratamiento de conducto simple', 200.00, 60, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(12, 6, 'Endodoncia multiradicular', 'Tratamiento de conducto complejo', 320.00, 90, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(13, 7, 'Corona dental', 'Aplicación de corona dental', 380.00, 60, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(14, 7, 'Prótesis parcial removible', 'Fabricación e instalación de prótesis parcial', 450.00, 90, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(15, 8, 'Tratamiento periodontal básico', 'Tratamiento básico de encías', 150.00, 45, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(16, 9, 'Radiografía panorámica', 'Radiografía dental completa', 80.00, 15, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00'),
(17, 10, 'Consulta pediátrica', 'Consulta especializada para niños', 60.00, 30, 1, '2024-01-01 08:00:00', '2024-01-01 08:00:00');

-- HISTORIAL DE PRECIOS DE TRATAMIENTOS
INSERT INTO treatment_price_history (id, treatment_id, price, start_date, end_date, created_at) VALUES
(1, 1, 45.00, '2024-01-01', '2024-02-29', '2024-01-01 08:00:00'),
(2, 1, 50.00, '2024-03-01', NULL, '2024-03-01 08:00:00'),
(3, 3, 65.00, '2024-01-01', '2024-03-31', '2024-01-01 08:00:00'),
(4, 3, 70.00, '2024-04-01', NULL, '2024-04-01 08:00:00'),
(5, 5, 480.00, '2024-01-01', '2024-04-30', '2024-01-01 08:00:00'),
(6, 5, 500.00, '2024-05-01', NULL, '2024-05-01 08:00:00'),
(7, 9, 280.00, '2024-01-01', '2024-05-31', '2024-01-01 08:00:00'),
(8, 9, 300.00, '2024-06-01', NULL, '2024-06-01 08:00:00');

-- PACIENTES
INSERT INTO patients (id, first_name, last_name, birthdate, gender, phone, email, address, registration_date, notes) VALUES
(1, 'María', 'González', '1985-06-15', 'F', '+34 612345678', 'maria.gonzalez@email.com', 'Calle Mayor 25, Madrid', '2024-01-10 10:30:00', 'Alergia a la penicilina'),
(2, 'Juan', 'Fernández', '1975-11-23', 'M', '+34 623456789', 'juan.fernandez@email.com', 'Av. Libertad 42, Barcelona', '2024-01-12 12:15:00', 'Hipertensión'),
(3, 'Carmen', 'Rodríguez', '1992-03-08', 'F', '+34 634567890', 'carmen.rodriguez@email.com', 'Plaza España 5, Sevilla', '2024-01-15 09:45:00', 'Sin alergias conocidas'),
(4, 'Antonio', 'López', '1968-08-30', 'M', '+34 645678901', 'antonio.lopez@email.com', 'Calle Sol 12, Valencia', '2024-01-18 16:20:00', 'Diabetes tipo 2'),
(5, 'Ana', 'Martínez', '1998-01-24', 'F', '+34 656789012', 'ana.martinez@email.com', 'Av. Mediterráneo 8, Málaga', '2024-01-20 11:10:00', ''),
(6, 'Pablo', 'Sánchez', '1980-07-17', 'M', '+34 667890123', 'pablo.sanchez@email.com', 'Calle Nueva 36, Bilbao', '2024-01-25 15:30:00', 'Sensibilidad dental'),
(7, 'Laura', 'Díaz', '1995-12-03', 'F', '+34 678901234', 'laura.diaz@email.com', 'Av. Principal 15, Zaragoza', '2024-02-02 10:45:00', ''),
(8, 'Roberto', 'García', '1965-05-20', 'M', '+34 689012345', 'roberto.garcia@email.com', 'Plaza Mayor 9, Alicante', '2024-02-05 14:20:00', 'Problemas cardíacos'),
(9, 'Elena', 'Pérez', '1990-09-28', 'F', '+34 690123456', 'elena.perez@email.com', 'Calle Ancha 19, Córdoba', '2024-02-10 09:15:00', 'Alergia al látex'),
(10, 'Miguel', 'Torres', '1972-04-12', 'M', '+34 601234567', 'miguel.torres@email.com', 'Av. Marina 27, Murcia', '2024-02-15 17:30:00', 'Propenso a sangrado');

-- HISTORIAL MÉDICO
INSERT INTO medical_records (id, patient_id, record_date, symptoms, diagnosis, treatment_plan, notes) VALUES
(1, 1, '2024-01-10 10:45:00', 'Dolor molar izquierdo superior', 'Caries profunda en pieza 26', 'Endodoncia y corona', 'Paciente nerviosa, considerar sedación leve'),
(2, 2, '2024-01-12 12:30:00', 'Sangrado de encías, mal aliento', 'Periodontitis moderada', 'Limpieza profunda y tratamiento periodontal', 'Recomendar cambio de cepillo y técnica'),
(3, 3, '2024-01-15 10:00:00', 'Dientes apiñados, mordida cruzada', 'Maloclusión clase II', 'Tratamiento ortodóntico con brackets', 'Paciente interesada en opciones estéticas'),
(4, 4, '2024-01-18 16:40:00', 'Dolor agudo al masticar', 'Fractura dental en pieza 36', 'Extracción y valoración de implante', 'Monitorear niveles de glucosa'),
(5, 5, '2024-01-20 11:30:00', 'Insatisfacción con color dental', 'Tinción por consumo de café', 'Blanqueamiento dental', ''),
(6, 6, '2024-01-25 15:45:00', 'Dolor al consumir frío o caliente', 'Hipersensibilidad dental generalizada', 'Aplicación de barniz de flúor y pasta desensibilizante', 'Revisión en 3 semanas'),
(7, 7, '2024-02-02 11:00:00', 'Ausencia de piezas posteriores', 'Edentulismo parcial', 'Prótesis parcial removible', 'Valorar implantes a futuro'),
(8, 1, '2024-02-05 09:30:00', 'Control post-tratamiento', 'Evolución favorable endodoncia', 'Finalizar corona', 'Sin molestias'),
(9, 8, '2024-02-05 14:40:00', 'Dolor e inflamación en zona molar', 'Absceso periapical agudo', 'Drenaje, antibióticos y posterior endodoncia', 'Prescripción ajustada por condición cardíaca'),
(10, 9, '2024-02-10 09:30:00', 'Deseo de mejorar estética dental', 'Diastema y ligera rotación dental', 'Carillas en piezas 11 y 21', 'Usar guantes sin látex');

-- CITAS
INSERT INTO appointments (id, patient_id, date, start_time, end_time, status, notes) VALUES
(1, 1, '2024-01-10', '10:30:00', '11:00:00', 'completada', 'Primera consulta'),
(2, 2, '2024-01-12', '12:15:00', '12:45:00', 'completada', 'Primera consulta'),
(3, 3, '2024-01-15', '09:45:00', '10:15:00', 'completada', 'Primera consulta'),
(4, 4, '2024-01-18', '16:20:00', '16:50:00', 'completada', 'Primera consulta, urgencia'),
(5, 5, '2024-01-20', '11:10:00', '11:40:00', 'completada', 'Primera consulta'),
(6, 1, '2024-01-22', '09:00:00', '10:30:00', 'completada', 'Inicio endodoncia'),
(7, 6, '2024-01-25', '15:30:00', '16:00:00', 'completada', 'Primera consulta'),
(8, 2, '2024-01-27', '10:00:00', '11:00:00', 'completada', 'Inicio limpieza profunda'),
(9, 7, '2024-02-02', '10:45:00', '11:15:00', 'completada', 'Primera consulta'),
(10, 1, '2024-02-05', '09:00:00', '10:00:00', 'completada', 'Finalización endodoncia'),
(11, 8, '2024-02-05', '14:20:00', '14:50:00', 'completada', 'Primera consulta, urgencia'),
(12, 3, '2024-02-08', '16:00:00', '17:30:00', 'completada', 'Colocación brackets'),
(13, 9, '2024-02-10', '09:15:00', '09:45:00', 'completada', 'Primera consulta'),
(14, 10, '2024-02-15', '17:30:00', '18:00:00', 'completada', 'Primera consulta'),
(15, 5, '2024-02-18', '11:00:00', '12:00:00', 'completada', 'Sesión blanqueamiento'),
(16, 3, '2024-03-08', '16:00:00', '16:30:00', 'completada', 'Ajuste brackets'),
(17, 1, '2024-03-12', '10:00:00', '11:00:00', 'completada', 'Colocación corona'),
(18, 4, '2024-03-15', '15:00:00', '15:45:00', 'completada', 'Extracción pieza 36'),
(19, 3, '2024-04-08', '16:00:00', '16:30:00', 'completada', 'Ajuste brackets'),
(20, 9, '2024-04-15', '09:30:00', '11:00:00', 'completada', 'Colocación carillas'),
(21, 7, '2024-04-20', '12:00:00', '13:30:00', 'completada', 'Prueba prótesis'),
(22, 3, '2024-05-08', '16:00:00', '16:30:00', 'completada', 'Ajuste brackets'),
(23, 7, '2024-05-15', '12:00:00', '13:00:00', 'completada', 'Entrega prótesis final'),
(24, 2, '2024-05-20', '11:00:00', '11:45:00', 'completada', 'Revisión periodontal'),
(25, 3, '2024-06-08', '16:00:00', '16:30:00', 'programada', 'Ajuste brackets'),
(26, 10, '2024-06-10', '17:00:00', '18:00:00', 'programada', 'Limpieza dental'),
(27, 5, '2024-06-12', '10:00:00', '10:30:00', 'programada', 'Revisión blanqueamiento'),
(28, 1, '2024-06-15', '09:00:00', '09:30:00', 'programada', 'Revisión semestral');

-- CITAS_TRATAMIENTOS
INSERT INTO appointment_treatments (id, appointment_id, treatment_id, quantity, price_applied, notes) VALUES
(1, 1, 1, 1, 45.00, 'Consulta inicial'),
(2, 2, 1, 1, 45.00, 'Consulta inicial'),
(3, 3, 1, 1, 45.00, 'Consulta inicial'),
(4, 4, 1, 1, 45.00, 'Consulta inicial urgencia'),
(5, 5, 1, 1, 45.00, 'Consulta inicial'),
(6, 6, 11, 1, 200.00, 'Endodoncia pieza 26'),
(7, 7, 1, 1, 50.00, 'Consulta inicial'),
(8, 8, 4, 1, 120.00, 'Limpieza profunda cuadrantes 1 y 2'),
(9, 9, 1, 1, 50.00, 'Consulta inicial'),
(10, 10, 11, 1, 200.00, 'Finalización endodoncia'),
(11, 11, 1, 1, 50.00, 'Consulta inicial urgencia'),
(12, 12, 5, 1, 480.00, 'Instalación de brackets'),
(13, 13, 1, 1, 50.00, 'Consulta inicial'),
(14, 14, 1, 1, 50.00, 'Consulta inicial'),
(15, 15, 9, 1, 280.00, 'Primera sesión blanqueamiento'),
(16, 16, 6, 1, 80.00, 'Primer ajuste mensual'),
(17, 17, 13, 1, 380.00, 'Colocación corona pieza 26'),
(18, 18, 7, 1, 100.00, 'Extracción pieza 36'),
(19, 19, 6, 1, 80.00, 'Segundo ajuste mensual'),
(20, 20, 10, 2, 700.00, 'Colocación carillas piezas 11 y 21'),
(21, 21, 14, 1, 450.00, 'Prueba prótesis parcial'),
(22, 22, 6, 1, 80.00, 'Tercer ajuste mensual'),
(23, 23, 14, 1, 0.00, 'Entrega final, incluido en precio anterior'),
(24, 24, 15, 1, 150.00, 'Revisión y mantenimiento periodontal'),
(25, 25, 6, 1, 80.00, 'Cuarto ajuste mensual'),
(26, 26, 3, 1, 70.00, 'Limpieza programada'),
(27, 27, 2, 1, 35.00, 'Revisión post-blanqueamiento');

-- PAGOS
INSERT INTO payments (id, appointment_id, amount, payment_date, payment_method, notes) VALUES
(1, 1, 45.00, '2024-01-10 11:05:00', 'tarjeta', 'Pago completo'),
(2, 2, 45.00, '2024-01-12 12:50:00', 'efectivo', 'Pago completo'),
(3, 3, 45.00, '2024-01-15 10:20:00', 'tarjeta', 'Pago completo'),
(4, 4, 45.00, '2024-01-18 16:55:00', 'transferencia', 'Pago completo'),
(5, 5, 45.00, '2024-01-20 11:45:00', 'tarjeta', 'Pago completo'),
(6, 6, 200.00, '2024-01-22 10:35:00', 'tarjeta', 'Pago completo'),
(7, 7, 50.00, '2024-01-25 16:05:00', 'efectivo', 'Pago completo'),
(8, 8, 120.00, '2024-01-27 11:05:00', 'tarjeta', 'Pago completo'),
(9, 9, 50.00, '2024-02-02 11:20:00', 'efectivo', 'Pago completo'),
(10, 10, 200.00, '2024-02-05 10:05:00', 'tarjeta', 'Pago completo'),
(11, 11, 50.00, '2024-02-05 14:55:00', 'transferencia', 'Pago completo'),
(12, 12, 240.00, '2024-02-08 17:35:00', 'tarjeta', 'Primer pago (50%)'),
(13, 13, 50.00, '2024-02-10 09:50:00', 'efectivo', 'Pago completo'),
(14, 14, 50.00, '2024-02-15 18:05:00', 'tarjeta', 'Pago completo'),
(15, 15, 280.00, '2024-02-18 12:05:00', 'tarjeta', 'Pago completo'),
(16, 16, 80.00, '2024-03-08 16:35:00', 'efectivo', 'Pago completo'),
(17, 12, 240.00, '2024-03-08 16:40:00', 'tarjeta', 'Segundo pago (50%)'),
(18, 17, 380.00, '2024-03-12 11:05:00', 'tarjeta', 'Pago completo'),
(19, 18, 100.00, '2024-03-15 15:50:00', 'efectivo', 'Pago completo'),
(20, 19, 80.00, '2024-04-08 16:35:00', 'tarjeta', 'Pago completo'),
(21, 20, 350.00, '2024-04-15 11:05:00', 'tarjeta', 'Primer pago (50%)'),
(22, 21, 225.00, '2024-04-20 13:35:00', 'transferencia', 'Primer pago (50%)'),
(23, 22, 80.00, '2024-05-08 16:35:00', 'efectivo', 'Pago completo'),
(24, 20, 350.00, '2024-05-10 10:00:00', 'tarjeta', 'Segundo pago (50%)'),
(25, 23, 225.00, '2024-05-15 13:05:00', 'transferencia', 'Segundo pago (50%)'),
(26, 24, 150.00, '2024-05-20 11:50:00', 'tarjeta', 'Pago completo');

-- HORARIO DE TRABAJO
INSERT INTO work_schedule (id, day_of_week, start_time, end_time, is_working_day) VALUES
(1, 1, '09:00:00', '14:00:00', 1), -- Lunes mañana
(2, 1, '16:00:00', '20:00:00', 1), -- Lunes tarde
(3, 2, '09:00:00', '14:00:00', 1), -- Martes mañana
(4, 2, '16:00:00', '20:00:00', 1), -- Martes tarde
(5, 3, '09:00:00', '14:00:00', 1), -- Miércoles mañana
(6, 3, '16:00:00', '20:00:00', 1), -- Miércoles tarde
(7, 4, '09:00:00', '14:00:00', 1), -- Jueves mañana
(8, 4, '16:00:00', '20:00:00', 1), -- Jueves tarde
(9, 5, '09:00:00', '14:00:00', 1), -- Viernes mañana
(10, 5, '16:00:00', '19:00:00', 1), -- Viernes tarde (hora reducida)
(11, 6, '10:00:00', '13:00:00', 1), -- Sábado mañana
(12, 7, NULL, NULL, 0);           -- Domingo no laborable

-- CONFIGURACIÓN DE EMAIL
INSERT INTO email_settings (id, smtp_server, smtp_port, username, password, sender_email, sender_name, signature) VALUES
(1, 'smtp.clinicadental.com', 587, 'notificaciones@clinicadental.com', 'P@ssw0rd!2024', 'notificaciones@clinicadental.com', 'Clínica Dental', 'Clínica Dental Sonrisas\nTel: +34 912345678\nwww.clinicadental.com');

-- PLANTILLAS DE EMAIL
INSERT INTO email_templates (id, name, subject, body, active) VALUES
(1, 'recordatorio_cita', 'Recordatorio de su cita en Clínica Dental', 'Estimado/a {{nombre_paciente}},\n\nLe recordamos que tiene una cita programada para el día {{fecha_cita}} a las {{hora_cita}}.\n\nPor favor, llegue 10 minutos antes de la hora programada. Si necesita cancelar o reprogramar, contáctenos con al menos 24 horas de antelación.\n\nSaludos cordiales,\n{{firma}}', 1),
(2, 'confirmacion_cita', 'Confirmación de cita en Clínica Dental', 'Estimado/a {{nombre_paciente}},\n\nSu cita ha sido confirmada para el día {{fecha_cita}} a las {{hora_cita}}.\n\nTratamiento(s): {{tratamientos}}\n\nLe esperamos en nuestra clínica.\n\nSaludos cordiales,\n{{firma}}', 1),
(3, 'agradecimiento_visita', 'Gracias por su visita a Clínica Dental', 'Estimado/a {{nombre_paciente}},\n\nQuisiéramos agradecerle por su visita el día {{fecha_cita}}.\n\nEsperamos que su experiencia haya sido satisfactoria. Si tiene alguna pregunta sobre su tratamiento o necesita programar una cita de seguimiento, no dude en contactarnos.\n\nSaludos cordiales,\n{{firma}}', 1),
(4, 'recordatorio_pago', 'Recordatorio de pago pendiente', 'Estimado/a {{nombre_paciente}},\n\nLe recordamos que tiene un pago pendiente por el tratamiento {{tratamiento}} realizado el {{fecha_tratamiento}} por un importe de {{importe_pendiente}} €.\n\nPor favor, regularice su situación lo antes posible.\n\nSaludos cordiales,\n{{firma}}', 1),
(5, 'felicitacion_cumpleanos', 'Feliz Cumpleaños desde Clínica Dental', 'Estimado/a {{nombre_paciente}},\n\nTodo el equipo de Clínica Dental le desea un muy feliz cumpleaños. Como regalo especial, le ofrecemos un 10% de descuento en su próxima limpieza dental si reserva durante este mes.\n\n¡Que tenga un día maravilloso!\n\nSaludos cordiales,\n{{firma}}', 1);

-- SEGUIMIENTO DE EMAILS
INSERT INTO email_tracking (id, appointment_id, sent_date, email_type, recipient_email, status, response_date, response_content) VALUES
(1, 25, '2024-06-06 09:00:00', 'recordatorio_cita', 'carmen.rodriguez@email.com', 'enviado', NULL, NULL),
(2, 26, '2024-06-08 09:00:00', 'recordatorio_cita', 'miguel.torres@email.com', 'enviado', '2024-06-08 10:15:00', 'Confirmo asistencia'),
(3, 27, '2024-06-10 09:00:00', 'recordatorio_cita', 'ana.martinez@email.com', 'enviado', '2024-06-08 10:15:00', 'Confirmo asistencia');

-- Continuación de SEGUIMIENTO DE EMAILS
INSERT INTO email_tracking (id, appointment_id, sent_date, email_type, recipient_email, status, response_date, response_content) VALUES
(4, 28, '2024-06-12 09:00:00', 'recordatorio_cita', 'maria.gonzalez@email.com', 'enviado', NULL, NULL),
(5, 12, '2024-02-05 18:00:00', 'confirmacion_cita', 'carmen.rodriguez@email.com', 'enviado', '2024-02-05 19:30:00', 'OK, gracias'),
(6, 20, '2024-04-10 10:00:00', 'confirmacion_cita', 'elena.perez@email.com', 'enviado', NULL, NULL),
(7, 15, '2024-02-17 12:00:00', 'recordatorio_cita', 'ana.martinez@email.com', 'enviado', '2024-02-17 12:30:00', 'Confirmado'),
(8, 1, '2024-01-10 18:00:00', 'agradecimiento_visita', 'maria.gonzalez@email.com', 'enviado', NULL, NULL),
(9, 2, '2024-01-12 18:00:00', 'agradecimiento_visita', 'juan.fernandez@email.com', 'enviado', NULL, NULL),
(10, 3, '2024-01-15 18:00:00', 'agradecimiento_visita', 'carmen.rodriguez@email.com', 'enviado', NULL, NULL),
(11, 5, '2024-01-24 09:00:00', 'felicitacion_cumpleanos', 'ana.martinez@email.com', 'enviado', '2024-01-24 10:45:00', '¡Muchas gracias!'),
(12, 8, '2024-05-20 09:00:00', 'felicitacion_cumpleanos', 'roberto.garcia@email.com', 'enviado', NULL, NULL),
(13, 17, '2024-03-11 09:00:00', 'recordatorio_cita', 'maria.gonzalez@email.com', 'enviado', '2024-03-11 11:20:00', 'Asistiré puntual'),
(14, 21, '2024-04-18 09:00:00', 'recordatorio_cita', 'laura.diaz@email.com', 'enviado', NULL, NULL),
(15, 22, '2024-05-05 09:00:00', 'recordatorio_cita', 'carmen.rodriguez@email.com', 'enviado', '2024-05-05 10:15:00', 'Confirmado');

-- Datos adicionales para pacientes (10 más)
INSERT INTO patients (id, first_name, last_name, birthdate, gender, phone, email, address, registration_date, notes) VALUES
(11, 'Sofía', 'Ruiz', '1988-02-14', 'F', '+34 612345679', 'sofia.ruiz@email.com', 'Calle Gran Vía 33, Madrid', '2024-03-01 10:20:00', 'Embarazada de 5 meses'),
(12, 'David', 'Hernández', '1979-07-22', 'M', '+34 623456780', 'david.hernandez@email.com', 'Av. Diagonal 125, Barcelona', '2024-03-05 11:45:00', 'Fuma ocasionalmente'),
(13, 'Isabel', 'Jiménez', '1993-11-05', 'F', '+34 634567891', 'isabel.jimenez@email.com', 'Plaza Nueva 7, Sevilla', '2024-03-10 16:30:00', ''),
(14, 'Francisco', 'Moreno', '1960-09-18', 'M', '+34 645678902', 'francisco.moreno@email.com', 'Calle Colón 22, Valencia', '2024-03-15 09:15:00', 'Problemas de coagulación'),
(15, 'Lucía', 'Álvarez', '1996-04-27', 'F', '+34 656789013', 'lucia.alvarez@email.com', 'Av. Andalucía 15, Málaga', '2024-03-20 14:00:00', ''),
(16, 'Javier', 'Romero', '1983-12-08', 'M', '+34 667890124', 'javier.romero@email.com', 'Calle Ledesma 8, Bilbao', '2024-04-02 17:45:00', 'Alergia a anestésicos con epinefrina'),
(17, 'Teresa', 'Navarro', '1975-06-30', 'F', '+34 678901235', 'teresa.navarro@email.com', 'Av. Independencia 42, Zaragoza', '2024-04-10 10:30:00', ''),
(18, 'Alberto', 'Molina', '1968-03-12', 'M', '+34 689012346', 'alberto.molina@email.com', 'Plaza del Ayuntamiento 5, Alicante', '2024-04-15 12:15:00', 'Hipertensión controlada'),
(19, 'Patricia', 'Gil', '1991-08-25', 'F', '+34 690123457', 'patricia.gil@email.com', 'Calle San Fernando 19, Córdoba', '2024-04-22 15:20:00', ''),
(20, 'Raúl', 'Ortega', '1977-01-19', 'M', '+34 601234568', 'raul.ortega@email.com', 'Av. Juan Carlos I 27, Murcia', '2024-05-05 09:45:00', 'Deportista profesional');

-- Más historial médico
INSERT INTO medical_records (id, patient_id, record_date, symptoms, diagnosis, treatment_plan, notes) VALUES
(11, 11, '2024-03-01 10:40:00', 'Dolor en muela del juicio', 'Pericoronaritis en pieza 18', 'Extracción programada post-parto', 'Solo tratamiento sintomático por embarazo'),
(12, 12, '2024-03-05 12:00:00', 'Mal aliento persistente', 'Cálculos subgingivales severos', 'Limpieza profunda y curetaje', 'Recomendar dejar de fumar'),
(13, 13, '2024-03-10 16:45:00', 'Dientes amarillos', 'Tinción extrínseca por té', 'Limpieza profesional y blanqueamiento', 'Paciente muy preocupada por estética'),
(14, 14, '2024-03-15 09:40:00', 'Movilidad dental', 'Periodontitis avanzada', 'Extracción de piezas móviles y prótesis', 'Coordinar con hematólogo'),
(15, 15, '2024-03-20 14:15:00', 'Deseo de ortodoncia invisible', 'Maloclusión clase I leve', 'Tratamiento con alineadores transparentes', ''),
(16, 16, '2024-04-02 18:00:00', 'Dolor agudo al frío', 'Caries profunda en pieza 35', 'Endodoncia con anestesia especial', 'Usar anestésico sin epinefrina'),
(17, 17, '2024-04-10 10:50:00', 'Ausencia múltiples piezas', 'Edentulismo parcial severo', 'Rehabilitación con implantes', 'Valorar estado óseo'),
(18, 18, '2024-04-15 12:30:00', 'Sensibilidad generalizada', 'Recesión gingival generalizada', 'Injertos de encía programados', 'Controlar presión arterial'),
(19, 19, '2024-04-22 15:35:00', 'Dientes pequeños', 'Microdoncia generalizada', 'Carillas estéticas completas', ''),
(20, 20, '2024-05-05 10:00:00', 'Fractura incisivo', 'Fractura complicada pieza 11', 'Endodoncia y reconstrucción con poste', 'Cuidado por traumatismos deportivos');

-- Más citas programadas
INSERT INTO appointments (id, patient_id, date, start_time, end_time, status, notes) VALUES
(29, 11, '2024-06-20', '11:00:00', '11:30:00', 'programada', 'Consulta seguimiento'),
(30, 12, '2024-06-22', '10:00:00', '11:30:00', 'programada', 'Limpieza profunda'),
(31, 13, '2024-06-25', '17:00:00', '18:00:00', 'programada', 'Sesión blanqueamiento'),
(32, 14, '2024-07-03', '09:30:00', '10:15:00', 'programada', 'Extracción pieza 32'),
(33, 15, '2024-07-05', '16:00:00', '17:00:00', 'programada', 'Entrega alineadores'),
(34, 16, '2024-07-10', '12:00:00', '13:00:00', 'programada', 'Endodoncia'),
(35, 17, '2024-07-12', '11:30:00', '12:00:00', 'programada', 'Consulta implantes'),
(36, 18, '2024-07-15', '10:00:00', '11:30:00', 'programada', 'Injerto gingival'),
(37, 19, '2024-07-18', '17:00:00', '18:30:00', 'programada', 'Preparación carillas'),
(38, 20, '2024-07-20', '09:00:00', '10:00:00', 'programada', 'Reconstrucción post-endodoncia');

-- Más tratamientos en citas
INSERT INTO appointment_treatments (id, appointment_id, treatment_id, quantity, price_applied, notes) VALUES
(28, 29, 2, 1, 35.00, 'Revisión post-embarazo'),
(29, 30, 4, 1, 120.00, 'Limpieza profunda cuadrantes 3 y 4'),
(30, 31, 9, 1, 300.00, 'Segunda sesión blanqueamiento'),
(31, 32, 8, 1, 250.00, 'Extracción quirúrgica pieza 32'),
(32, 33, 5, 1, 500.00, 'Entrega alineadores fase 1'),
(33, 34, 12, 1, 320.00, 'Endodoncia multiradicular pieza 35'),
(34, 35, 1, 1, 50.00, 'Consulta inicial implantes'),
(35, 36, 15, 1, 150.00, 'Injerto gingival sector anterior'),
(36, 37, 10, 8, 2800.00, 'Preparación para 8 carillas'),
(37, 38, 13, 1, 380.00, 'Reconstrucción post-endodoncia pieza 11');

-- Más pagos programados
INSERT INTO payments (id, appointment_id, amount, payment_date, payment_method, notes) VALUES
(27, 29, 35.00, '2024-06-20 11:35:00', 'tarjeta', 'Pago completo'),
(28, 30, 120.00, '2024-06-22 11:35:00', 'efectivo', 'Pago completo'),
(29, 31, 150.00, '2024-06-25 18:05:00', 'tarjeta', 'Pago inicial 50%'),
(30, 32, 125.00, '2024-07-03 10:20:00', 'transferencia', 'Pago inicial 50%'),
(31, 33, 250.00, '2024-07-05 17:05:00', 'tarjeta', 'Pago inicial 50%'),
(32, 34, 160.00, '2024-07-10 13:05:00', 'efectivo', 'Pago inicial 50%'),
(33, 35, 50.00, '2024-07-12 12:05:00', 'tarjeta', 'Pago completo'),
(34, 36, 75.00, '2024-07-15 11:35:00', 'transferencia', 'Pago inicial 50%'),
(35, 37, 1400.00, '2024-07-18 18:35:00', 'tarjeta', 'Pago inicial 50%'),
(36, 38, 190.00, '2024-07-20 10:05:00', 'efectivo', 'Pago inicial 50%');