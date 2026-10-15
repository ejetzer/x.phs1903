Communication entre Arduino et Python
=======================================

.. warning::

   Il est recommandé de compléter les :doc:`../tuto` avant de consulter et d'utiliser cette section.

.. sourcecode:: c++
   :linenos:
   :caption: ardcom.ino
   :name: lst:ardcom.ino

   #include <serie.h>
   #include <broche.h>
   #include <chrono.h>

   phs::ListeBroche<uint16_t> broche (A0, 200);
   phs::Broche del (13);
   phs::Chrono mesure (10);
   phs::LigneSerie serie (115200);

   void print_broche () {
     for ( uint8_t i = broche.begin (); i < broche.end (); i++)
     {
       broche.pos (i);
       serie.print (broche);
       serie.ln ();
     }
   }

   void setup ()
   {
     serie.setup ();
     broche.setup ();
   }

   void loop ()
   {
     serie.loop ();

     if ( mesure.loop () )
     {
       broche.loop ();
     }

     if ( serie.available () )
     {
       String cmd = serie.cmd ();
       if ( ( cmd == "A0" ) || ( cmd == "14" ) )
       {
         serie.println(broche);
       }
       else if ( cmd == "13" )
       {
         del.regler( !del.valeur () );
       }
     }

     if ( broche.is_full () )
     {
       print_broche ();
       broche.empty ();
     }
   }

.. sourcecode:: c++
   :linenos:
   :caption: std_ardcom.ino
   :name: lst:std_ardcom.ino

   #define BROCHE A0
   #define DEL 13
   #define DELAI 10

   uint16_t temps[200];
   uint16_t broche[200];
   uint16_t chrono = 0;
   uint8_t index = 0;
   uint16_t dernier;

   void print_broche()
   {
     for ( uint8_t i = 0; i < 200; i++)
     {
       Serial.print("t:");
       Serial.print(temps[i]);
       Serial.print("\tA0:");
       Serial.println(broche[i]);
     }
   }

   void setup ()
   {
     Serial.begin(115200);
     pinMode(BROCHE, INPUT_PULLUP);
     pinMode(DEL, OUTPUT);
   }

   void loop ()
   {
     if ( Serial.available() )
     {
       String cmd = Serial.readStringUntil("\n");
       if ( ( cmd == "A0" ) || ( cmd == "14" ) )
       {
         Serial.print("t:");
         Serial.print(millis());
         Serial.print("\tA0:");
         Serial.println(analogRead(BROCHE));
       }
       else if ( cmd == "13" )
       {
         digitalWrite(DEL, !digitalRead(DEL));
       }
     }

     if ( ( millis() - dernier ) > DELAI )
     {
       broche[index] = analogRead(BROCHE);
       index++;
       dernier = millis();
     }

     if ( index == 200 )
     {
       print_broche();
       index = 0;
     }
   }

.. sourcecode:: python
   :linenos:
   :caption: ardcom.py
   :name: lst:ardcom.py

   from xphs1903.utils.serial import ArduinoNanoEvery

   with ArduinoNanoEvery(baudrate=9600) as com:
       while True:
           try:
               val = com.next(block=False, parse=True)
               if val is None or val == {}:
                 pass
           except KeyboardInterrupt:
               break

.. sourcecode:: python
   :linenos:
   :caption: std_ardcom.py
   :name: lst:std_ardcom.py

   from serial import serial_from_url

