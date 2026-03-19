# Project Blueprint – Starter Kit  

**Nombre del proyecto:**  
DocSimplify AI – Asistente IA de Simplificación de Documentos para Dislexia y TDAH

**Cliente:**  
Cliente piloto (Universidad / Empresa inclusiva – ejemplo: Universidad XYZ o corporativo con programa de diversidad)

## 1 Contexto

**1. Propósito del sistema**  
Resolver la sobrecarga cognitiva que enfrentan personas con dislexia y TDAH al leer documentos densos (PDF, Word, contratos, syllabi, reportes). El sistema transfosrma cualquier documento en versiones claras, estructuradas y personalizadas (nivel de lectura A1-C1), con resúmenes en bullets, explicaciones calmadas (“Reduje esta frase porque…”) y audio/visuales accesibles. Está diseñado para estudiantes, profesionales y docentes, mejorando comprensión lectora en 40-60% y reduciendo tiempo de lectura en 50%.

**2. Actores involucrados**  

- Usuario Neurodiverso (Estudiante o Empleado con dislexia/TDAH)  
- Docente / Profesor / Gestor de equipo  
- Administrador de Preferencias (configura perfiles de accesibilidad)  
- Sistema externo (Office 365 / Teams – integración futura)

**3. Objetivos del Proyecto**  

1. Mejorar comprensión lectora y retención en usuarios con dislexia y TDAH (meta: +40-60% según estudios 2025-2026).  
2. Reducir tiempo de procesamiento de documentos en 50% y ansiedad asociada a lectura.  
3. Cumplir estándares WCAG 2.2 y prácticas de IA responsable (lenguaje calmado, explicabilidad total).  
4. Almacenar preferencias de accesibilidad de forma segura y adaptar el sistema con el tiempo.  
5. Generar impacto medible en educación y workplace inclusivo (productividad +20-35%).

## 2 Casos de Uso

**2.1 Acciones clave por actor**

**Actor:** Usuario Neurodiverso (Estudiante/Empleado con dislexia o TDAH)  
**Acciones**  

1. Subir documento (PDF/Word/texto).  
2. Seleccionar nivel de lectura deseado (A1-A2 hasta C1).  
3. Recibir versión simplificada + resumen bullets + audio.  
4. Ver explicaciones calmadas de cada cambio.

**Actor:** Docente / Profesor / Gestor  
**Acciones**  

1. Subir material académico o reporte.  
2. Generar versiones múltiples para diferentes perfiles de alumnos/equipo.  
3. Descargar resúmenes y métricas de mejora esperada.

**Actor:** Administrador de Preferencias  
**Acciones**  

1. Configurar y guardar perfiles de accesibilidad seguros.  
2. Revisar historial de uso y ajustes automáticos.

**2.2 y 2.3 Diagrama Casos de Uso** (descripción textual – se puede dibujar en Miro/Lucidchart)

Nombre del Sistema: **DocSimplify AI**

- Usuario Neurodiverso → Subir documento → Seleccionar nivel → Recibir simplificación + audio  
- Docente → Subir material → Generar versiones múltiples → Descargar  
- Administrador → Configurar preferencias → Revisar historial  

(Flujo principal centrado en el círculo “Simplificar y adaptar documento” conectado a los tres actores).

## 3 Diagrama de Flujo

**3.1 Identifica el Flujo Principal**

**Actor:** Usuario Neurodiverso  
**Flujo Principal**  

1. Subir documento.  
2. Elegir nivel de lectura y preferencias.  
3. Recibir versión simplificada + explicaciones.  
4. Escuchar audio y marcar como entendido.

**Actor:** Docente  
**Flujo Principal**  

1. Subir material.  
2. Seleccionar perfiles de alumnos.  
3. Generar y descargar versiones adaptadas.

**Actor:** Administrador  
**Flujo Principal**  

1. Revisar y ajustar perfiles globales.

**3.2 Diagrama** (descripción secuencial)

Usuario Neurodiverso → [Subir documento] → [Procesar con IA] → [Generar versión A2 + bullets + audio] → [Mostrar explicaciones calmadas]  
↓ (opcional)  
Docente → [Revisar y aprobar versiones]  
Administrador → [Guardar preferencias para próximos usos]

## 4 Requerimientos Funcionales

**4.1 Requerimientos Principales**  
• El sistema debe permitir subir documentos (PDF, Word, texto largo).  
• El sistema debe simplificar texto a nivel de lectura ajustable (A1-C1) usando Plain Language.  
• El sistema debe generar resúmenes en bullets + versión Immersive Reader con audio.  
• El sistema debe mostrar explicaciones calmadas de cada simplificación.

**4.2 Requerimientos Secundarios**  
• El sistema debe almacenar preferencias de accesibilidad de forma segura.  
• El sistema debe detectar automáticamente si el documento es denso y sugerir nivel recomendado.  
• El sistema debe generar preguntas de comprensión opcionales para verificar retención.

**4.3 y 4.4 Agrupa requerimientos y enuméralos**  
**Área 1 – Ingesta y Procesamiento** (RF-01 a RF-03)  
**Área 2 – Simplificación y Salida** (RF-04 a RF-06)  
**Área 3 – Preferencias y Adaptación** (RF-07 a RF-08)  
**Área 4 – Explicabilidad y IA Responsable** (RF-09)

## 5 Story Mapping

**Épica:** Simplificación de Documentos  
**Historia:** Como Usuario Neurodiverso (dislexia/TDAH) quiero subir un documento y recibir una versión simplificada nivel A2 para poder comprenderlo sin sobrecarga cognitiva.  
**Criterios de Aceptación:**  

- Documento procesado en <10 segundos.  
- Versión generada con frases <15 palabras y vocabulario familiar.  
- Audio Immersive Reader disponible.  
- Explicación calmada visible.

**Épica:** Resúmenes y Apoyo Concentración  
**Historia:** Como Docente quiero generar múltiples versiones de un mismo material para diferentes alumnos para ahorrar tiempo y mejorar inclusión.  
**Criterios de Aceptación:**  

- Hasta 3 niveles simultáneos.  
- Resúmenes bullets exportables.  
- Métricas de mejora estimada mostradas.

**Épica:** Gestión de Preferencias  
**Historia:** Como Administrador quiero guardar perfiles de accesibilidad seguros para que el sistema se adapte automáticamente en usos futuros.  
**Criterios de Aceptación:**  

- Preferencias encriptadas.  
- Historial de ajustes visible.  
- Cumplimiento GDPR/WCAG.
