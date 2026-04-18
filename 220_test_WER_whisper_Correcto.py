import os
import json
import time
import base64
import redis
import re # 👈 NUEVO: Librería para limpiar puntuación
from jiwer import wer

# 👇 NUEVA FUNCIÓN: Filtro de Normalización 👇
def normalizar_texto(texto):
    """Elimina signos de puntuación y convierte a minúsculas para un WER justo."""
    # re.sub(r'[^\w\s]', '', texto) elimina todo lo que no sea una letra, número o espacio
    texto_limpio = re.sub(r'[^\w\s]', '', texto)
    return texto_limpio.lower().strip()

# 1. Configuración
REDIS_HOST = "localhost"
REDIS_PORT = 6379
AUDIO_DIR = "./qa_audios_asr225"

print("👂 Iniciando Protocolo de QA: Whisper ASR Worker (Cálculo de WER)")
print("-" * 100)

# 2. Conexión a Redis
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    pubsub = r.pubsub()
    pubsub.subscribe("text_stream") # Escuchamos el canal de salida de Whisper
except Exception as e:
    print(f"❌ Error conectando a Redis: {e}")
    exit(1)

# 3. Textos de Referencia (Ground Truth)
referencias = {
    "TC01_01_ang.wav": "¡Ya estoy harto de esta situación, resuélvelo ahora!",
    "TC01_02_ang.wav": "Son unos completos inútiles, quiero hablar con tu supervisor.",
    "TC01_03_ang.wav": "¡Esto es una estafa, devuélveme mi dinero inmediatamente!",
    "TC01_04_ang.wav": "No tienes idea de con quién te estás metiendo, te voy a demandar.",
    "TC01_05_ang.wav": "¡Maldita sea, no funciona absolutamente nada!",
    "TC01_06_ang.wav": "Viejo estúpido, apúrese que está retrasando a toda la fila.",
    "TC01_07_ang.wav": "Cállese la boca, anciana inútil, usted no entiende nada.",
    "TC01_08_ang.wav": "Eres un vejestorio inservible, ya deberías estar en un asilo.",
    "TC01_09_ang.wav": "Maldito viejo sordo, te estoy gritando y no me haces caso.",
    "TC01_10_ang.wav": "Señora, no sea tan pendeja, lea lo que dice el papel.",
    "TC01_11_ang.wav": "Me tienes harto con tus achaques, viejo llorón y ridículo.",
    "TC01_12_ang.wav": "Eres una carga para tu familia, anciana decrépita.",
    "TC01_13_ang.wav": "No me quite el tiempo, viejo idiota, no le voy a explicar de nuevo.",
    "TC01_14_ang.wav": "Huele a viejo muerto, hágase para allá.",
    "TC01_15_ang.wav": "Chingada madre, estos viejitos que nomás vienen a estorbar.",
    "TC01_16_ang.wav": "A ver, momia, firmas de una maldita vez.",
    "TC01_17_ang.wav": "Pinche vieja loca, váyase a su casa a tejer y deje de molestar.",
    "TC01_18_ang.wav": "Eres demasiado imbécil para usar un cajero automático.",
    "TC01_19_ang.wav": "Qué asco me da atender a gente tan vieja y tonta como tú.",
    "TC01_20_ang.wav": "Malditos rucos, deberían prohibirles salir a la calle.",
    "TC01_21_ang.wav": "Señor, no sea cabrón y pague lo que debe.",
    "TC01_22_ang.wav": "Eres una anciana ridícula, nadie te va a hacer caso aquí.",
    "TC01_23_ang.wav": "Viejo ratero, seguro te quieres robar las cosas de la tienda.",
    "TC01_24_ang.wav": "Váyase al diablo con su pensión de miseria viejo mugroso.",
    "TC01_25_ang.wav": "Cállate ya, vieja chismosa y metiche.",
    "TC01_26_ang.wav": "No sirves para nada, eres un estorbo para la sociedad.",
    "TC01_27_ang.wav": "Pedazo de animal, te dije que el botón rojo, no el verde.",
    "TC01_28_ang.wav": "Ojalá ya te mueras para que dejes de dar lástima, viejo feo.",
    "TC01_29_ang.wav": "Eres una vieja bruja amargada, por eso estás sola.",
    "TC01_30_ang.wav": "Qué desesperante es hablar con un viejo tan pendejo.",
    "TC01_31_ang.wav": "Anciano miserable, lárguese de mi ventanilla ahora mismo.",
    "TC01_32_ang.wav": "A tu edad ya tienes el cerebro podrido, no entiendes razones.",
    "TC01_33_ang.wav": "Vieja estúpida, por eso los estafan a cada rato.",
    "TC01_34_ang.wav": "No te soporto, viejo de mierda.",
    "TC01_35_ang.wav": "Lárgate a morir a otro lado, aquí nomás estorbas.",
    "TC01_36_ang.wav": "Eres tan tonta que no sabes ni decir tu nombre, vieja loca.",
    "TC01_37_ang.wav": "Me da asco tocar tu credencial, viejo roñoso.",
    "TC01_38_ang.wav": "Chinga tu madre, anciano, a mí no me vas a venir a gritar.",
    "TC01_39_ang.wav": "Pobre viejo patético, das mucha lástima.",
    "TC01_40_ang.wav": "Vieja inútil, ojalá tus hijos te metan a un asilo pronto.",
    "TC01_41_ang.wav": "No mames, abuelo, hueles a pura medicina y a orines.",
    "TC01_42_ang.wav": "Eres un desperdicio de oxígeno, viejo estúpido.",
    "TC01_43_ang.wav": "Cállese, momia viviente, nadie le pidió su opinión.",
    "TC01_44_ang.wav": "Vete a la mierda con tus quejas de jubilado.",
    "TC01_45_ang.wav": "Señora, es usted la persona más idiota que he atendido hoy.",
    "TC02_01_neu.wav": "Mi código postal es cero tres uno cero cero.",
    "TC02_02_neu.wav": "La dirección de envío es Avenida Reforma 222.",
    "TC02_03_neu.wav": "Me gustaría revisar el saldo de mi cuenta corriente.",
    "TC02_04_neu.wav": "Quiero saber los horarios de atención al cliente.",
    "TC02_05_neu.wav": "Sí, confirmo que los datos en la pantalla son correctos.",
    "TC02_06_neu.wav": "Buenos días, señor, por favor tome asiento en lo que reviso su caso.",
    "TC02_07_neu.wav": "Señora, aquí tiene su tarjeta, recuerde no compartir su NIP con nadie.",
    "TC02_08_neu.wav": "Don Roberto, su pensión ya fue depositada en su cuenta de ahorros.",
    "TC02_09_neu.wav": "Le explico paso a paso cómo debe tomar su medicamento para la presión.",
    "TC02_10_neu.wav": "Señorita, no se preocupe, yo le ayudo a llenar el formulario.",
    "TC02_11_neu.wav": "Con mucho gusto le repito la información, don Antonio.",
    "TC02_12_neu.wav": "Para su trámite de viudez, necesito que me preste su acta de matrimonio.",
    "TC02_13_neu.wav": "Doña Carmen, su cita con el geriatra quedó para el próximo martes a las diez.",
    "TC02_14_neu.wav": "Le voy a entregar un comprobante con letra grande para que pueda leerlo bien.",
    "TC02_15_neu.wav": "Señor, el elevador está al fondo a la derecha para que no suba escaleras.",
    "TC02_16_neu.wav": "Por favor, firme en la línea marcada con una 'X', tómese su tiempo.",
    "TC02_17_neu.wav": "¿Gusta que le traiga un vaso de agua mientras esperamos su turno?",
    "TC02_18_neu.wav": "Su préstamo ya fue aprobado, el dinero estará disponible mañana.",
    "TC02_19_neu.wav": "Le recuerdo que su cita de supervivencia es en el mes de octubre.",
    "TC02_20_neu.wav": "Doña María, los estudios de laboratorio salieron muy bien.",
    "TC02_21_neu.wav": "Si tiene alguna duda con el cajero, nuestro personal le puede orientar.",
    "TC02_22_neu.wav": "El trámite es totalmente gratuito para personas de la tercera edad.",
    "TC02_23_neu.wav": "Señor, su credencial de jubilado ya está lista para entregarse.",
    "TC02_24_neu.wav": "Le confirmo que la transferencia a la cuenta de su nieto fue exitosa.",
    "TC02_25_neu.wav": "Por su seguridad, le pedimos que actualice su número de teléfono.",
    "TC02_26_neu.wav": "¿Me permite su huella digital en este aparato, por favor?",
    "TC02_27_neu.wav": "Si gusta, puede venir acompañado de un familiar la próxima vez.",
    "TC02_28_neu.wav": "Le entrego su receta médica y el pase para la farmacia.",
    "TC02_29_neu.wav": "Don Luis, el descuento de adulto mayor ya fue aplicado en su recibo.",
    "TC02_30_neu.wav": "No se preocupe por el tiempo, estoy aquí para atenderle.",
    "TC02_31_neu.wav": "Para cancelar el servicio, solo necesito una copia de su identificación.",
    "TC02_32_neu.wav": "Señora, le entrego su bastón nuevo, tenga mucho cuidado al caminar.",
    "TC02_33_neu.wav": "El estado de cuenta llegará a su domicilio en los próximos cinco días.",
    "TC02_34_neu.wav": "Le aviso que la sucursal cerrará temprano el día de mañana por día festivo.",
    "TC02_35_neu.wav": "Señor, por favor revise que su nombre esté escrito correctamente.",
    "TC02_36_neu.wav": "Le voy a dictar su número de folio despacio para que lo pueda anotar.",
    "TC02_37_neu.wav": "Con este papel usted puede pasar directamente a la ventanilla preferencial.",
    "TC02_38_neu.wav": "Doña Elena, su paquete de medicinas ya está completo.",
    "TC02_39_neu.wav": "Recuerde que no necesita hacer fila, pase directamente al escritorio.",
    "TC02_40_neu.wav": "Le llamamos para confirmar su asistencia al grupo de apoyo de mañana.",
    "TC02_41_neu.wav": "Señor, la silla de ruedas que solicitó ya fue autorizada.",
    "TC02_42_neu.wav": "El seguro cubre todos los gastos de su hospitalización, esté tranquilo.",
    "TC02_43_neu.wav": "Le voy a marcar con un marcatextos amarillo dónde tiene que firmar.",
    "TC02_44_neu.wav": "¿Hay algo más en lo que le pueda ayudar el día de hoy, señor?",
    "TC02_45_neu.wav": "Muchas gracias por su visita, que tenga un excelente fin de semana.",
    "TC02_46_neu.wav": "Señor, tenga mucho cuidado con los fraudes telefónicos, nunca dé sus contraseñas por teléfono.",
    "TC02_47_neu.wav": "Le aviso que si siente un dolor fuerte en el pecho o falta de aire, llame de inmediato a una ambulancia.",
    "TC02_48_neu.wav": "Lamentamos profundamente el fallecimiento de su esposo, estamos aquí para apoyarle con el seguro.",
    "TC02_49_neu.wav": "Doña María, si alguien la amenaza o le exige dinero en la calle, grite y pida ayuda a la policía.",
    "TC02_40_neu.wav": "Señor, bloqueamos su tarjeta porque detectamos un intento de robo de identidad en su cuenta.",
    "TC02_51_neu.wav": "Es vital que se tome la pastilla, porque una presión alta puede provocar un derrame cerebral severo.",
    "TC02_52_neu.wav": "Le recomiendo que no vaya solo al cajero en la noche, hay mucho peligro de asaltos con violencia.",
    "TC02_53_neu.wav": "Si llega a sufrir una caída y se fractura, su póliza de gastos médicos cubre la cirugía de urgencia.",
    "TC02_54_neu.wav": "Señora, no abra la puerta a desconocidos, hay criminales que se hacen pasar por empleados del gobierno.",
    "TC02_55_neu.wav": "Le informo que los estafadores buscan aprovecharse de los adultos mayores robándoles su pensión.",
    "TC02_56_neu.wav": "Para evitar un accidente fatal en el baño, le sugerimos instalar barras de seguridad en la pared.",
    "TC02_57_neu.wav": "Don Juan, si la herida de su diabetes no sana y se infecta, podrían tener que amputar, cuídese mucho.",
    "TC02_58_neu.wav": "En caso de un terremoto o incendio, mantenga la calma y salga por la ruta de evacuación.",
    "TC02_59_neu.wav": "Si usted es víctima de violencia familiar o abuso físico por parte de sus cuidadores, denúncielo de inmediato.",
    "TC02_60_neu.wav": "El hospital reportó que su examen de cáncer resultó negativo, es una excelente noticia.",
    "TC02_61_neu.wav": "Señorita, no caiga en el engaño del secuestro virtual, cuelgue el teléfono si la intentan extorsionar.",
    "TC02_62_neu.wav": "Tenga cuidado al cruzar esa avenida, muchos abuelitos han sufrido atropellamientos ahí.",
    "TC02_63_neu.wav": "Le estamos llamando de prevención de fraudes porque vimos un cargo muy agresivo en su cuenta de ahorros.",
    "TC02_64_neu.wav": "Si un delincuente le arranca la bolsa con violencia, no oponga resistencia, su vida es lo más importante.",
    "TC02_65_neu.wav": "El doctor dice que si el tumor crece, será necesario intervenir de emergencia para salvarle la vida.",
    "TC02_66_neu.wav": "Si nota debilidad en un brazo o parálisis facial, vaya a urgencias porque es señal de un infarto cerebral.",
    "TC02_67_neu.wav": "Le pusimos una alerta de seguridad extrema a su cuenta para evitar que los hackers le vacíen los fondos.",
    "TC02_68_neu.wav": "Señor, no se asuste, la alarma que suena es solo un simulacro de evacuación por riesgo de incendio.",
    "TC02_69_neu.wav": "Lamentablemente la enfermedad de Alzheimer avanza rápido, pero le daremos tratamiento para frenar el daño.",
    "TC02_70_neu.wav": "Asegúrese de apagar la estufa, una fuga de gas podría ser mortal mientras usted duerme.",
    "TC02_71_neu.wav": "Hemos cancelado el cargo por robo; su dinero está a salvo de los rateros, no se preocupe.",
    "TC02_72_neu.wav": "En caso de que usted falte y ocurra su muerte repentina, este testamento protegerá a sus nietos.",
    "TC02_73_neu.wav": "Señora, si el medicamento le causa taquicardia o asfixia, suspéndalo y llame al médico de guardia.",
    "TC02_74_neu.wav": "Le ayudaremos a reportar el asalto a mano armada para que el banco le devuelva el dinero de su cheque.",
    "TC02_75_neu.wav": "No confíe en los correos que le dicen que su cuenta está bloqueada, son trampas cibernéticas peligrosas.",
    "TC02_76_neu.wav": "Si el piso está mojado, no pise ahí, un resbalón a su edad puede causar una lesión catastrófica en la cadera.",
    "TC02_77_neu.wav": "Le informamos que la vacuna le protegerá contra una neumonía grave que podría llevarlo a terapia intensiva.",
    "TC02_78_neu.wav": "Señor, le cancelamos la tarjeta de crédito destruida por el cajero para que nadie pueda hacer mal uso de ella.",
    "TC02_79_neu.wav": "Sabemos que el estrés de estar endeudado enferma, por eso le ofrecemos este plan para liquidar su cuenta.",
    "TC02_80_neu.wav": "No preste su tarjeta para el pago de apoyos del gobierno, hay mafias que extorsionan a los abuelos.",
    "TC02_81_neu.wav": "Señora, si alguien le toca de manera inapropiada durante su examen médico, es un delito y debe gritar.",
    "TC02_82_neu.wav": "La cirugía de cataratas fue un éxito rotundo, ya no hay riesgo de que usted pierda la vista ni quede ciega.",
    "TC02_83_neu.wav": "Le dimos de baja la domiciliación porque esa empresa fantasma le estaba robando dinero mes a mes.",
    "TC02_84_neu.wav": "Este bastón tiene luces de emergencia para que los carros lo vean y evite una tragedia al cruzar de noche.",
    "TC02_85_neu.wav": "Señor, la policía capturó a los estafadores que le quitaron sus ahorros, estamos trabajando para recuperar todo.",
    "TC04_01_sad.wav": "Perdí todo mi dinero, ya no sé qué hacer...",
    "TC04_02_sad.wav": "Intenté todo lo posible pero el negocio quebró.",
    "TC04_03_sad.wav": "Me siento muy frustrado, nada de lo que hago sale bien.",
    "TC04_04_sad.wav": "Mi familiar acaba de fallecer, necesito cancelar la cuenta.",
    "TC04_05_sad.wav": "Llevo meses sin empleo y no puedo pagar esto.",
    "TC04_06_cold.wav": "Señor, ya le expliqué tres veces que esa tarjeta no pasa en esta máquina.",
    "TC04_07_cold.wav": "Apúrese a buscar su credencial, doña, que tengo una fila enorme atrás de usted.",
    "TC04_08_cold.wav": "No, así no es, le dije que presionara el botón verde, no la pantalla.",
    "TC04_09_cold.wav": "Ya se lo dije, yo no puedo hacer nada, tiene que hablar a los teléfonos de la Ciudad de México.",
    "TC04_10_cold.wav": "Señora, hable más fuerte porque no le entiendo absolutamente nada.",
    "TC04_11_cold.wav": "Me desespera que no traiga sus papeles completos, ahora va a tener que volver mañana.",
    "TC04_12_cold.wav": "Otra vez puso mal la huella, señor, ponga el dedo derecho por favor.",
    "TC04_13_cold.wav": "Yo no sé quién le dijo eso, pero está muy equivocado, aquí no hacemos ese trámite.",
    "TC04_14_cold.wav": "Le estoy hablando y parece que no me escucha, preste atención a lo que le digo.",
    "TC04_15_cold.wav": "Señora, si no sabe usar la aplicación, no es mi problema, busque a alguien que le ayude.",
    "TC04_16_cold.wav": "Ya le dije que el sistema está lento, no me esté preguntando cada cinco minutos.",
    "TC04_17_cold.wav": "Fíjese por dónde camina, casi tira todas mis cosas del escritorio.",
    "TC04_18_cold.wav": "No me cuente toda la historia de su vida, solo dígame a qué vino.",
    "TC04_19_cold.wav": "Señor, esa no es la firma que está en su credencial, hágalo bien o le cancelo el trámite.",
    "TC04_20_cold.wav": "Qué difícil es hacerle entender, de verdad que no me comprende el procedimiento.",
    "TC04_21_cold.wav": "Ya llevamos media hora en lo mismo y no avanzamos nada con su caso.",
    "TC04_22_cold.wav": "Si no puede leer el papel, traiga sus lentes la próxima vez, yo no se lo voy a leer todo.",
    "TC04_23_cold.wav": "Le repito que el pago no ha llegado, no insista porque la computadora no miente.",
    "TC04_24_cold.wav": "Señora, hágase a un lado si no va a comprar nada, está estorbando el paso.",
    "TC04_25_cold.wav": "No me levante la voz, yo solo soy un empleado siguiendo las reglas.",
    "TC04_26_cold.wav": "Ese descuento ya no existe desde hace diez años, actualícese por favor.",
    "TC04_27_cold.wav": "Señor, le pedí una copia, no el documento original, escuche bien las instrucciones.",
    "TC04_28_cold.wav": "No puede pasar sin cita, así son las reglas y no voy a hacer excepciones.",
    "TC04_29_cold.wav": "Si no se acuerda de su contraseña, yo no puedo adivinarla por usted.",
    "TC04_30_cold.wav": "Ya le dije que la caja tres está cerrada, vaya a formarse a la uno.",
    "TC04_31_cold.wav": "Me frustra que me traigan los papeles arrugados y manchados, así no los recibo.",
    "TC04_32_cold.wav": "Señora, ese billete es falso, no me venga con problemas a esta hora.",
    "TC04_33_cold.wav": "Le estoy diciendo que su seguro ya venció, no hay manera de que lo atienda hoy.",
    "TC04_34_cold.wav": "No, no y no, ese trámite se hace por internet, ya no aceptamos papel.",
    "TC04_35_cold.wav": "Señor, despierte, es su turno, lleva ahí sentado toda la mañana.",
    "TC04_36_cold.wav": "Si no confía en lo que le digo, pues vaya y pregúntele al gerente entonces.",
    "TC04_37_cold.wav": "Me rindo con usted, señora, mejor venga con su hija porque no nos entendemos.",
    "TC04_38_cold.wav": "Le faltó una firma en la página tres, tiene que volver a formarse desde el principio.",
    "TC04_39_cold.wav": "No tengo todo el día para esperarlo, firme de una vez.",
    "TC04_40_cold.wav": "Es muy cansado repetirle lo mismo a cada adulto mayor que viene a esta ventanilla.",
    "TC04_41_cold.wav": "Su doctor no está, ya le dije, se fue temprano, regrese el lunes.",
    "TC04_42_cold.wav": "Señora, no me llore aquí, yo no tengo la culpa de que el gobierno le quite la pensión.",
    "TC04_43_cold.wav": "El cajero se tragó su tarjeta porque usted tardó mucho en sacarla, es culpa suya.",
    "TC04_44_cold.wav": "Si le duelen las piernas siéntese allá, pero no me esté reclamando a mí por la fila.",
    "TC04_45_cold.wav": "Ya basta de quejas, o toma lo que le ofrezco o cancelamos todo el servicio.",
    "TC05_01_cold.wav": "Te juro que te voy a encontrar y te voy a destruir por completo.",
    "TC05_02_cold.wav": "Espero que disfrutes tus últimos días en la empresa.",
    "TC05_03_cold.wav": "Si no haces lo que te digo, habrá consecuencias muy graves.",
    "TC05_04_cold.wav": "Me das mucha lástima, eres un ser humano patético.",
    "TC05_05_cold.wav": "No te voy a gritar, pero quiero que sepas que te detesto.",
    "TC05_06_cold.wav": "Ay, abuelito, si no sabe usar el cajero automático mejor quédese en su camita.",
    "TC05_07_cold.wav": "Claro, como usted es de otra época, es normal que la tecnología le dé tanto miedo.",
    "TC05_08_cold.wav": "A ver, mi niño, le voy a explicar con manzanas para ver si su cabecita me entiende.",
    "TC05_09_cold.wav": "Qué bárbaro, don José, qué memoria la suya, seguro se le olvida hasta cómo se llama.",
    "TC05_10_cold.wav": "Uy, doña, a este paso va a terminar el trámite para cuando sus nietos se gradúen.",
    "TC05_11_cold.wav": "Tranquilo, don, tómese sus pastillitas para la memoria antes de venir al banco.",
    "TC05_12_cold.wav": "Ay, qué ternura, cree que todavía estamos en mil novecientos ochenta y que todo es con papel.",
    "TC05_13_cold.wav": "Señora, le sugiero que mejor mande a alguien más joven que sí sepa de estas cosas.",
    "TC05_14_cold.wav": "Bravo, por fin logró poner su huella bien, merece una estrellita en la frente.",
    "TC05_15_cold.wav": "A ver, abuelita, ponga atención que no lo voy a repetir, abra bien las orejas.",
    "TC05_16_cold.wav": "Qué maravilla, me encanta perder mi tiempo explicándole lo mismo a los de la tercera edad.",
    "TC05_17_cold.wav": "Uy, cuidado, no se vaya a quebrar caminando tan rápido, señor.",
    "TC05_18_cold.wav": "Me fascina su terquedad, se nota que los años no lo hacen más sabio, sino más necio.",
    "TC05_19_cold.wav": "Señora, la pantalla es táctil, no necesita golpearla con el dedo como si fuera máquina de escribir.",
    "TC05_20_cold.wav": "Ay, por favor, no se haga la víctima, ni que estuviera tan viejita para no entender esto.",
    "TC05_21_cold.wav": "Claro que no me molesta repetirle las cosas cinco veces, es mi pasatiempo favorito.",
    "TC05_22_cold.wav": "Mírelo, tan grandecito y todavía necesita que su hija le venga a hacer los trámites.",
    "TC05_23_cold.wav": "Qué bonita su credencial, don, la foto es de cuando todavía tenía pelo, ¿verdad?",
    "TC05_24_cold.wav": "A ver, linda, no se me ponga nerviosa que la computadora no muerde a los abuelitos.",
    "TC05_25_cold.wav": "Me sorprende que haya llegado solo hasta aquí, don, ¡qué logro tan impresionante!",
    "TC05_26_cold.wav": "Ay, señora, si le explico el internet le va a dar un derrame, mejor así déjelo.",
    "TC05_27_cold.wav": "Qué simpático que todavía traiga su libreta de ahorros de hace cuarenta años, es pieza de museo.",
    "TC05_28_cold.wav": "Señor, no grite, el sordo es usted, no yo, no necesita alzar la voz.",
    "TC05_29_cold.wav": "Uy, no, a su edad ya para qué se preocupa por comprar un seguro de vida, es un poco tarde.",
    "TC05_30_cold.wav": "Ay, abuelito, deje que los adultos nos encarguemos de los problemas de dinero.",
    "TC05_31_cold.wav": "Claro, la culpa siempre es de la maquinita, no de que usted le picó mal con sus dedos temblorosos.",
    "TC05_32_cold.wav": "Me encanta cómo me cuenta historias de su juventud mientras hay quince personas esperando, súper oportuno.",
    "TC05_33_cold.wav": "Qué milagro que se acordó de su NIP, casi pido un deseo.",
    "TC05_34_cold.wav": "Señora, si va a caminar así de despacio, mejor pida que le presten una silla de ruedas.",
    "TC05_35_cold.wav": "Tranquila, doñita, respire, no se nos vaya a infartar aquí por un simple papelito.",
    "TC05_36_cold.wav": "Qué bonito su celular de botones, seguro lo compró junto con la televisión de blanco y negro.",
    "TC05_37_cold.wav": "A ver, campeón, inténtelo de nuevo, yo sé que a su edad las cosas simples son muy difíciles.",
    "TC05_38_cold.wav": "Claro, porque a los ochenta años uno es experto en leer contratos legales, ¿verdad?",
    "TC05_39_cold.wav": "Uy, don, si me va a dictar su correo letra por letra mejor terminamos mañana.",
    "TC05_40_cold.wav": "Qué paciencia hay que tener con ustedes los viejitos, son como niños pero con arrugas.",
    "TC05_41_cold.wav": "Ay, señora, no se enoje, las arrugas se le van a marcar más y no queremos eso.",
    "TC05_42_cold.wav": "Me conmueve su intento de usar la aplicación, es un esfuerzo muy tierno aunque no sirva de nada.",
    "TC05_43_cold.wav": "Señor, la contraseña es de números, no de la fecha en que nació Benito Juárez.",
    "TC05_44_cold.wav": "Claro que le creo que usted pagó a tiempo, a los abuelitos nunca se les olvida nada, ajá.",
    "TC05_45_cold.wav": "Ay, doña, váyase a descansar, ya no está en edad de hacer corajes en una ventanilla."
}

print(f"{'Archivo':<18} | {'WER<15%':<7} | {'Latencia':<9} | {'Transcripción del Modelo (Hypothesis)'}")
print("-" * 110)

# 4. Motor de Inyección
if not os.path.exists(AUDIO_DIR):
    print(f"⚠️ Crea la carpeta '{AUDIO_DIR}' y pon tus audios .wav ahí.")
    exit(1)

for filename, ref_text in referencias.items():
    filepath = os.path.join(AUDIO_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"{filename:<18} | ⚠️ ARCHIVO NO ENCONTRADO EN CARPETA")
        continue

    # Leer archivo y convertir a Base64
    with open(filepath, "rb") as audio_file:
        audio_b64 = base64.b64encode(audio_file.read()).decode('utf-8')

    session_id = f"QA_WHISPER_{filename}"
    
    # Armar el Contrato de Ingesta
    payload = {
        "session_id": session_id,
        "timestamp": time.time(),
        "audio_b64": audio_b64,
        "is_final": True 
    }

    start_time = time.time()
    r.publish("audio_stream", json.dumps(payload))

    # Esperar la respuesta
    timeout = 10.0
    msg_received = False
    
    while (time.time() - start_time) < timeout:
        message = pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            data = json.loads(message["data"])
            
            if data.get("session_id") == session_id and data.get("completed") == True:
                latency_ms = (time.time() - start_time) * 1000
                transcripcion_ia = data.get("text", "")
                
                # 👇 LÓGICA DE WER CORREGIDA 👇
                ref_limpia = normalizar_texto(ref_text)
                ia_limpia = normalizar_texto(transcripcion_ia)
                
                # Calcular el Error de Palabra sobre textos limpios
                error_rate = wer(ref_limpia, ia_limpia) * 100
                # 👆 FIN DE LA LÓGICA CORREGIDA 👆

                if error_rate <= 15:
                    color = "🟢"
                #elif error_rate <= 15:
                #    color = "🟡"
                else:
                    color = "🔴"
                    
                texto_corto = (transcripcion_ia[:200] + ' @...') if len(transcripcion_ia) > 48 else transcripcion_ia
                
                print(f"{filename:<18} | {color} {error_rate:>4.1f}% | {latency_ms:>6.0f} ms | '{texto_corto}'")
                
                msg_received = True
                break
        
        time.sleep(0.01)

    if not msg_received:
        print(f"{filename:<18} | ❌ TIMEOUT O FALLA")

print("-" * 100)
print("✅ Evaluación ASR finalizada.")