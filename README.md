# PartesTeclea (prototipo)

Escribe en la pantalla **Procesos 2DO. JUZGADO** los datos de los partes ya revisados en ParteScan, siguiendo el orden del
tabulador. **Nunca pulsa «Aceptar»**: tú revisas cada causa y la aceptas.

1. En ParteScan revisa los partes y pulsa **Datos para tecleo (.json)**.
2. Ejecuta `PartesTeclea.exe partes-para-tecleo.json` (o `--simular` para ver qué escribiría sin tocar nada).
3. Para cada parte abre una causa nueva, deja el cursor en el Rol y sigue las instrucciones. En el modo paso a paso espera F9 antes de cada campo (sin quitarle el foco al sistema; ESC para parar).
   Si aparece un mensaje del sistema (por ejemplo «Vehículo existente, desea cargar los datos?»), el programa se detiene y lo respondes tú.

Estado: prototipo sin probar contra el sistema real. Pendientes: actuario (depende del último dígito del rol), oficina emisora
de Carabineros, combos de infracción y tipo de vehículo. Se calibra probando una causa de prueba.
