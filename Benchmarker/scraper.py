from bs4 import BeautifulSoup
import requests
import pymysql
from sshtunnel import SSHTunnelForwarder
from datetime import date
import re
import pandas as pd
import time

iHavanas = ["https://www.ihavanas.com/details.php?ptype=cigars&pid=Acid",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Aguila",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=AJ%20Fernandez",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Alec%20Bradley",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Avo",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Camacho",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Davidoff",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Deadwood",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=E.P.%20Carrillo",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Illusione",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Liga",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Oliva",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Plasencia",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Rocky%20Patel",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Toscano",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Bolivar",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Cohiba",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Combinaciones",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Cuaba",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Davidoff",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Diplomaticos",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=El%20Rey%20Del%20Mundo",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Fonseca",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=H.Upmann",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Hoyo%20de%20Monterrey",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Jose%20L.%20Piedra",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Juan%20Lopez",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=La%20Flor%20De%20Cano",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=La%20Gloria%20Cubana",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Montecristo",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=MYSTERY%20BOX",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Partagas",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Por%20Larranaga",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Punch",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Quai%20D%27orsay",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Quintero%20Y%20Hermano",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Rafael%20Gonzalez",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Ramon%20Allones",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Romeo%20Y%20Julieta",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Saint%20Luis%20Rey",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=San%20Cristobal%20De%20La%20Habana",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Sancho%20Panza",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Seleccion",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Trinidad",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Vegas%20Robaina",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Vegueros"
            ]

COH = ["https://www.cigarsofhabanos.com/cigars-bolivar",
       "https://www.cigarsofhabanos.com/cigars-cohiba",
       "https://www.cigarsofhabanos.com/cigars-combinaciones",
       "https://www.cigarsofhabanos.com/cigars-cuaba",
       "https://www.cigarsofhabanos.com/cigars-diplomaticos",
       "https://www.cigarsofhabanos.com/cigars-el-rey-del-mundo",
       "https://www.cigarsofhabanos.com/cigars-fonseca",
       "https://www.cigarsofhabanos.com/cigars-guantanamera",
       "https://www.cigarsofhabanos.com/cigars-h.upmann",
       "https://www.cigarsofhabanos.com/cigars-hoyo-de-monterrey",
       "https://www.cigarsofhabanos.com/cigars-jose-l.-piedra",
       "https://www.cigarsofhabanos.com/cigars-juan-lopez",
       "https://www.cigarsofhabanos.com/cigars-la-flor-de-cano",
       "https://www.cigarsofhabanos.com/cigars-la-gloria-cubana",
       "https://www.cigarsofhabanos.com/cigars-montecristo",
       "https://www.cigarsofhabanos.com/cigars-partagas",
       "https://www.cigarsofhabanos.com/cigars-por-larranaga",
       "https://www.cigarsofhabanos.com/cigars-punch",
       "https://www.cigarsofhabanos.com/cigars-quai-dorsay",
       "https://www.cigarsofhabanos.com/cigars-quintero-y-hermano",
       "https://www.cigarsofhabanos.com/cigars-rafael-gonzalez",
       "https://www.cigarsofhabanos.com/cigars-ramon-allones",
       "https://www.cigarsofhabanos.com/cigars-romeo-y-julieta",
       "https://www.cigarsofhabanos.com/cigars-saint-luis-rey",
       "https://www.cigarsofhabanos.com/cigars-san-cristobal-de-la-habana",
       "https://www.cigarsofhabanos.com/cigars-sancho-panza",
       "https://www.cigarsofhabanos.com/cigars-seleccion",
       "https://www.cigarsofhabanos.com/cigars-trinidad",
       "https://www.cigarsofhabanos.com/cigars-variety-packs",
       "https://www.cigarsofhabanos.com/cigars-vegas-robaina",
       "https://www.cigarsofhabanos.com/cigars-vegueros",
       "https://www.cigarsofhabanos.com/cigars-vintage",
       "https://www.cigarsofhabanos.com/cigars-acid",
       "https://www.cigarsofhabanos.com/cigars-aging-room",
       "https://www.cigarsofhabanos.com/cigars-aj-fernandez",
       "https://www.cigarsofhabanos.com/cigars-alec-bradley",
       "https://www.cigarsofhabanos.com/cigars-ambrosia",
       "https://www.cigarsofhabanos.com/cigars-arturo-fuente",
       "https://www.cigarsofhabanos.com/cigars-balmoral",
       "https://www.cigarsofhabanos.com/cigars-c-r",
       "https://www.cigarsofhabanos.com/cigars-camacho",
       "https://www.cigarsofhabanos.com/cigars-deadwood",
       "https://www.cigarsofhabanos.com/cigars-don-pepin-garcia-cuban-classic",
       "https://www.cigarsofhabanos.com/cigars-don-pepin-garcia-original",
       "https://www.cigarsofhabanos.com/cigars-don-pepin-garcia-series-jj",
       "https://www.cigarsofhabanos.com/cigars-drew-estate",
       "https://www.cigarsofhabanos.com/cigars-dunhill",
       "https://www.cigarsofhabanos.com/cigars-e-p-carrillo",
       "https://www.cigarsofhabanos.com/cigars-factory-smoke",
       "https://www.cigarsofhabanos.com/cigars-flor-de-las-antillas",
       "https://www.cigarsofhabanos.com/cigars-florida-sun-grown",
       "https://www.cigarsofhabanos.com/cigars-gurkha",
       "https://www.cigarsofhabanos.com/cigars-herrera-esteli",
       "https://www.cigarsofhabanos.com/cigars-hirochi-robaina",
       "https://www.cigarsofhabanos.com/cigars-illusione",
       "https://www.cigarsofhabanos.com/cigars-isla-del-sol",
       "https://www.cigarsofhabanos.com/cigars-jaime-garcia-reserva-especial",
       "https://www.cigarsofhabanos.com/cigars-joya",
       "https://www.cigarsofhabanos.com/cigars-kentucky-fire-cured",
       "https://www.cigarsofhabanos.com/cigars-kentucky-fire-sweets",
       "https://www.cigarsofhabanos.com/cigars-la-galera",
       "https://www.cigarsofhabanos.com/cigars-la-vieja-habana",
       "https://www.cigarsofhabanos.com/cigars-larutan",
       "https://www.cigarsofhabanos.com/cigars-latelier",
       "https://www.cigarsofhabanos.com/cigars-liga",
       "https://www.cigarsofhabanos.com/cigars-muwat",
       "https://www.cigarsofhabanos.com/cigars-my-father",
       "https://www.cigarsofhabanos.com/cigars-nica-rustica",
       "https://www.cigarsofhabanos.com/cigars-norteno",
       "https://www.cigarsofhabanos.com/cigars-oliva",
       "https://www.cigarsofhabanos.com/cigars-padron",
       "https://www.cigarsofhabanos.com/cigars-pappy-van-winkle-tradition",
       "https://www.cigarsofhabanos.com/cigars-pipe-tobacco",
       "https://www.cigarsofhabanos.com/cigars-plasencia",
       "https://www.cigarsofhabanos.com/cigars-rocky-patel",
       "https://www.cigarsofhabanos.com/cigars-tabak-especial-medio",
       "https://www.cigarsofhabanos.com/cigars-tabak-especial-oscuro",
       "https://www.cigarsofhabanos.com/cigars-tatuaje",
       "https://www.cigarsofhabanos.com/cigars-torcedor-1492",
       "https://www.cigarsofhabanos.com/cigars-toscano",
       ]

Neptune = ["https://www.neptunecigar.com/1502-cigar",
           "https://www.neptunecigar.com/601-cigar",
           "https://www.neptunecigar.com/ace-cigar",
           "https://www.neptunecigar.com/acid-cigar",
           "https://www.neptunecigar.com/adventura-cigar",
           "https://www.neptunecigar.com/aganorsa-cigar",
           "https://www.neptunecigar.com/aging-room-cigar",
           "https://www.neptunecigar.com/aj-fernandez-cigar",
           "https://www.neptunecigar.com/aladino-cigar",
           "https://www.neptunecigar.com/alcazar-cigar",
           "https://www.neptunecigar.com/alec-bradley-cigar",
           "https://www.neptunecigar.com/ambrosia-cigar",
           "https://www.neptunecigar.com/american-stogies-cigar",
           "https://www.neptunecigar.com/archetype-cigar",
           "https://www.neptunecigar.com/arturo-fuente-cigar",
           "https://www.neptunecigar.com/ashton-cigar",
           "https://www.neptunecigar.com/asylum-cigar",
           "https://www.neptunecigar.com/atabey-cigar",
           "https://www.neptunecigar.com/avo-cigar",
           "https://www.neptunecigar.com/baccarat-cigar",
           "https://www.neptunecigar.com/back2back-cigar",
           "https://www.neptunecigar.com/balmoral-cigar",
           "https://www.neptunecigar.com/blackbird-cigar",
           "https://www.neptunecigar.com/blanco-cigar",
           "https://www.neptunecigar.com/bolivar-cigar",
           "https://www.neptunecigar.com/brick-house-cigar",
           "https://www.neptunecigar.com/cain-cigar",
           "https://www.neptunecigar.com/caldwell-cigar",
           "https://www.neptunecigar.com/camacho-cigar",
           "https://www.neptunecigar.com/cao-cigar",
           "https://www.neptunecigar.com/carlos-torano-cigar",
           "https://www.neptunecigar.com/casa-cuevas-cigar",
           "https://www.neptunecigar.com/casa-de-garcia-cigar",
           "https://www.neptunecigar.com/casa-magna-cigar",
           "https://www.neptunecigar.com/casdagli-cigar",
           "https://www.neptunecigar.com/cc-cigar",
           "https://www.neptunecigar.com/cle-cigar",
           "https://www.neptunecigar.com/cohiba-cigar",
           "https://www.neptunecigar.com/cornelius-and-anthony-cigar",
           "https://www.neptunecigar.com/crowned-heads-cigar",
           "https://www.neptunecigar.com/crowned-heads-juarez-cigar",
           "https://www.neptunecigar.com/cuban-aristocrat-cigar",
           "https://www.neptunecigar.com/cuesta-rey-cigar",
           "https://www.neptunecigar.com/cumpay-cigar",
           "https://www.neptunecigar.com/cusano-cigar",
           "https://www.neptunecigar.com/dapper-cigars-cigar",
           "https://www.neptunecigar.com/davidoff-cigar",
           "https://www.neptunecigar.com/deadwood-cigar",
           "https://www.neptunecigar.com/debonaire-cigar",
           "https://www.neptunecigar.com/diamond-crown-cigar",
           "https://www.neptunecigar.com/diesel-cigar",
           "https://www.neptunecigar.com/don-diego-cigar",
           "https://www.neptunecigar.com/don-lino-cigar",
           "https://www.neptunecigar.com/don-pepin-cigar",
           "https://www.neptunecigar.com/don-tomas-cigar",
           "https://www.neptunecigar.com/drew-estate-cigar",
           "https://www.neptunecigar.com/drew-estate-larutan-cigar",
           "https://www.neptunecigar.com/drunk-chicken-cigar",
           "https://www.neptunecigar.com/dunbarton-tobacco-cigar",
           "https://www.neptunecigar.com/edition-one-cigar",
           "https://www.neptunecigar.com/eiroa-cigar",
           "https://www.neptunecigar.com/el-credito-cigar",
           "https://www.neptunecigar.com/el-gueguense-cigar",
           "https://www.neptunecigar.com/el-reloj-cigar",
           "https://www.neptunecigar.com/el-rey-del-mundo-cigar",
           "https://www.neptunecigar.com/el-viejo-continente-cigar",
           "https://www.neptunecigar.com/emperors-cut-cigar",
           "https://www.neptunecigar.com/ep-carrillo-cigar",
           "https://www.neptunecigar.com/epic-cigar",
           "https://www.neptunecigar.com/espinosa-cigar",
           "https://www.neptunecigar.com/excalibur-cigar",
           "https://www.neptunecigar.com/factory-smokes-cigar",
           "https://www.neptunecigar.com/factory-throwouts-cigar",
           "https://www.neptunecigar.com/ferio-tego-cigar",
           "https://www.neptunecigar.com/fernando-leon-family-cigar",
           "https://www.neptunecigar.com/flor-de-las-antillas-cigar",
           "https://www.neptunecigar.com/flor-de-oliva-cigar",
           "https://www.neptunecigar.com/flor-de-selva-cigar",
           "https://www.neptunecigar.com/florida-sun-grown-by-drew-estate-cigar",
           "https://www.neptunecigar.com/fonseca-cigar",
           "https://www.neptunecigar.com/foundation-cigar",
           "https://www.neptunecigar.com/foundry-cigar",
           "https://www.neptunecigar.com/fratello-cigar",
           "https://www.neptunecigar.com/gispert-cigar",
           "https://www.neptunecigar.com/gran-habano-cigar",
           "https://www.neptunecigar.com/guardian-of-the-farm-cigar",
           "https://www.neptunecigar.com/gurkha-cigar",
           "https://www.neptunecigar.com/h-upmann-cigar",
           "https://www.neptunecigar.com/harvester-cigar",
           "https://www.neptunecigar.com/havana-q-cigar",
           "https://www.neptunecigar.com/hav-a-tampa-jewels-cigar",
           "https://www.neptunecigar.com/helix-cigar",
           "https://www.neptunecigar.com/henry-clay-cigar",
           "https://www.neptunecigar.com/herrera-esteli-cigar",
           "https://www.neptunecigar.com/highclere-castle-cigar",
           "https://www.neptunecigar.com/hiram-and-solomon-cigar",
           "https://www.neptunecigar.com/honduran-nude-cigar",
           "https://www.neptunecigar.com/hoyo-de-monterrey-cigar",
           "https://www.neptunecigar.com/hr-cigar",
           "https://www.neptunecigar.com/hvc-cigar",
           "https://www.neptunecigar.com/ilegal-cigar",
           "https://www.neptunecigar.com/illusione-cigar",
           "https://www.neptunecigar.com/indian-motorcycle-cigar",
           "https://www.neptunecigar.com/isla-del-sol-cigar",
           "https://www.neptunecigar.com/island-jim-cigar",
           "https://www.neptunecigar.com/jc-newman-cigar",
           "https://www.neptunecigar.com/jaime-garcia-cigar",
           "https://www.neptunecigar.com/java-cigar",
           "https://www.neptunecigar.com/jfr-cigar",
           "https://www.neptunecigar.com/joya-de-nicaragua-cigar",
           "https://www.neptunecigar.com/kafie-1901-cigar",
           "https://www.neptunecigar.com/kristoff-cigar",
           "https://www.neptunecigar.com/la-antiguedad-cigar",
           "https://www.neptunecigar.com/la-aroma-de-cuba-cigar",
           "https://www.neptunecigar.com/la-aurora-cigar",
           "https://www.neptunecigar.com/la-barba-cigar",
           "https://www.neptunecigar.com/la-boheme-cigar",
           "https://www.neptunecigar.com/la-duena-cigar",
           "https://www.neptunecigar.com/la-estrella-cubana-cigar",
           "https://www.neptunecigar.com/la-flor-dominicana-lfd-cigar",
           "https://www.neptunecigar.com/la-fontana-cigar",
           "https://www.neptunecigar.com/la-galera-cigar",
           "https://www.neptunecigar.com/la-gianna-cigar",
           "https://www.neptunecigar.com/la-gloria-cubana-cigar",
           "https://www.neptunecigar.com/la-gran-llave-cigar",
           "https://www.neptunecigar.com/la-palina-cigar",
           "https://www.neptunecigar.com/la-vieja-habana-cigar",
           "https://www.neptunecigar.com/laranja-cigar",
           "https://www.neptunecigar.com/lars-tetens-cigar",
           "https://www.neptunecigar.com/las-cabrillas-cigar",
           "https://www.neptunecigar.com/las-calaveras-cigar",
           "https://www.neptunecigar.com/l-atelier-cigar",
           "https://www.neptunecigar.com/leon-jimenes-cigar",
           "https://www.neptunecigar.com/liga-privada-cigar",
           "https://www.neptunecigar.com/liga-undercrown-cigar",
           "https://www.neptunecigar.com/litto-gomez-cigar",
           "https://www.neptunecigar.com/los-caidos-cigar",
           "https://www.neptunecigar.com/lostandfound-cigar",
           "https://www.neptunecigar.com/luciano-cigar",
           "https://www.neptunecigar.com/m1-cigar",
           "https://www.neptunecigar.com/macanudo-cigar",
           "https://www.neptunecigar.com/matilde-cigar",
           "https://www.neptunecigar.com/mbombay-cigar",
           "https://www.neptunecigar.com/micallef-cigar",
           "https://www.neptunecigar.com/mombacho-cigar",
           "https://www.neptunecigar.com/montecristo-cigar",
           "https://www.neptunecigar.com/muestra-de-saka-cigar",
           "https://www.neptunecigar.com/murcielago-cigar",
           "https://www.neptunecigar.com/muwat-cigar",
           "https://www.neptunecigar.com/my-father-cigar",
           "https://www.neptunecigar.com/nat-cicco-cigar",
           "https://www.neptunecigar.com/nat-sherman-cigar",
           "https://www.neptunecigar.com/national-brand-cigar",
           "https://www.neptunecigar.com/neptune-cigar",
           "https://www.neptunecigar.com/nestor-miranda-cigar",
           "https://www.neptunecigar.com/neya-cigar",
           "https://www.neptunecigar.com/nica-rustica-cigar",
           "https://www.neptunecigar.com/nub-cigar",
           "https://www.neptunecigar.com/odyssey-cigar",
           "https://www.neptunecigar.com/oliva-cigar",
           "https://www.neptunecigar.com/oliveros-cigar",
           "https://www.neptunecigar.com/onyx-cigar",
           "https://www.neptunecigar.com/oscar-valladares-cigar",
           "https://www.neptunecigar.com/osok-cigar",
           "https://www.neptunecigar.com/padilla-cigar",
           "https://www.neptunecigar.com/padron-cigar",
           "https://www.neptunecigar.com/pappy-van-winkle-cigar",
           "https://www.neptunecigar.com/partagas-cigar",
           "https://www.neptunecigar.com/patoro-cigar",
           "https://www.neptunecigar.com/perdomo-cigar",
           "https://www.neptunecigar.com/perla-del-mar-cigar",
           "https://www.neptunecigar.com/pichardo-cigar",
           "https://www.neptunecigar.com/plasencia-cigar",
           "https://www.neptunecigar.com/por-larranaga-cigar",
           "https://www.neptunecigar.com/psyko-seven-cigar",
           "https://www.neptunecigar.com/punch-cigar",
           "https://www.neptunecigar.com/quesada-cigar",
           "https://www.neptunecigar.com/quorum-cigar",
           "https://www.neptunecigar.com/ramon-allones-cigar",
           "https://www.neptunecigar.com/rancho-luna-cigar",
           "https://www.neptunecigar.com/recluse-cigar",
           "https://www.neptunecigar.com/rocky-patel-cigar",
           "https://www.neptunecigar.com/roma-craft-cigar",
           "https://www.neptunecigar.com/romeo-y-julieta-cigar",
           "https://www.neptunecigar.com/room-101-cigar",
           "https://www.neptunecigar.com/rough-rider-cigar",
           "https://www.neptunecigar.com/saga-cigar",
           "https://www.neptunecigar.com/saint-luis-rey-cigar",
           "https://www.neptunecigar.com/san-cristobal-cigar",
           "https://www.neptunecigar.com/san-jeronimo-cigar",
           "https://www.neptunecigar.com/san-lotano-cigar",
           "https://www.neptunecigar.com/sancho-panza-cigar",
           "https://www.neptunecigar.com/secret-blend-of-cuba-cigar",
           "https://www.neptunecigar.com/sin-compromiso-cigar",
           "https://www.neptunecigar.com/sindicato-cigar",
           "https://www.neptunecigar.com/sosa-cigar",
           "https://www.neptunecigar.com/southern-draw-cigar",
           "https://www.neptunecigar.com/tabacos-baez-cigar",
           "https://www.neptunecigar.com/tabak-especial-cigar",
           "https://www.neptunecigar.com/tabernacle-cigar",
           "https://www.neptunecigar.com/tampa-trolleys-cigar",
           "https://www.neptunecigar.com/tatascan-cigar",
           "https://www.neptunecigar.com/tatiana-cigar",
           "https://www.neptunecigar.com/tatuaje-cigar",
           "https://www.neptunecigar.com/te-amo-cigar",
           "https://www.neptunecigar.com/the-american-cigar",
           "https://www.neptunecigar.com/the-circus-cigar",
           "https://www.neptunecigar.com/the-griffin-s-cigar",
           "https://www.neptunecigar.com/the-repeater-cigar",
           "https://www.neptunecigar.com/toscano-cigar",
           "https://www.neptunecigar.com/trader-jack-s-cigar",
           "https://www.neptunecigar.com/trinidad-cigar",
           "https://www.neptunecigar.com/vegafina-cigar",
           "https://www.neptunecigar.com/villa-zamorano-cigar",
           "https://www.neptunecigar.com/villiger-cigar",
           "https://www.neptunecigar.com/viva-la-vida-cigar",
           "https://www.neptunecigar.com/warfighter-tobacco-cigar",
           "https://www.neptunecigar.com/warped-cigar",
           "https://www.neptunecigar.com/wynwood-hills-cigar",
           "https://www.neptunecigar.com/zino-cigar",
           ]

MySQL_hostname = 'localhost'  # MySQL Host
sql_username = 'remoteAccess'  # Username
sql_password = 'lpf9dmWmi7@kdl'  # os.environ.get('sql_password') #Password
sql_main_database = 'wordpress'  # Database Name
sql_port = 3306
ssh_host = '206.189.3.154'  # SSH Host
ssh_user = 'root'  # SSH Username
ssh_port = 22
sql_ip = '1.1.1.1.1'
ssh_pass = 'we@dflG0QfL32F'

# variable to keep track of execution time
start_time = time.time()

with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_password=ssh_pass,
        ssh_username=ssh_user,
        remote_bind_address=(MySQL_hostname, sql_port)) as tunnel:
    conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                           passwd=sql_password, db=sql_main_database,
                           port=tunnel.local_bind_port)

    today = date.today()
    cursor = conn.cursor()
    query = "INSERT INTO scraper (ExtractionDate, Product, ProductType, Competitor, $) values (%s, %s, %s, %s, %s)"
    for urls in iHavanas:
        res = requests.get(urls).text
        doc = BeautifulSoup(res, "html.parser")
        name_box = doc.find_all(class_="product_name")
        price_box = doc.find_all(class_="current_price")
        box_type = doc.find_all(string=re.compile("Box"))
        for name_box, box_type, price_box in zip(name_box, box_type, price_box):
            val = (today, name_box.string, box_type, "IH", float(price_box.string[3:]))
            cursor.execute(query, val)
    print("iHavana Scrape done")

    for urls in COH:
        res = requests.get(urls).text
        doc = BeautifulSoup(res, "html.parser")
        tds = doc.find('td', valign="top", style="padding-left:8px;")
        try:
            tbody = tds.find('table', width="100%", border="0", cellspacing="0", cellpadding="0")
        except AttributeError:
            pass
        for td in tbody.find_all('td', align="left", valign="top"):
            try:
                name = td.find('span', class_=re.compile("^product")).string[1:]
                b_type = td.find(string=re.compile("Box")).string[1:]
                price = float(td.find(class_="pricetxt").find('strong').string.split('$')[1])
                val = (today, name, b_type, "CH", price)
                cursor.execute(query, val)
            except AttributeError:
                pass
    print("COH Scrape done")

    for urls in Neptune:
        res = requests.get(urls).text
        doc = BeautifulSoup(res, "html.parser")
        for product in doc.find_all('div', class_="product_item"):
            name = product.find('h2', itemprop="name")
            for box, price in zip(product.find_all(class_="product_table_cells lbup"),
                                  product.find_all('span', itemprop="price")):
                try:
                    val = (today, name.string, box.string, "NT", float(price.string.split('$')[1]))
                    cursor.execute(query, val)
                except AttributeError:
                    try:
                        val = (today, name.string, "", "NT", float(price.string.split('$')[1]))
                        cursor.execute(query, val)
                    except AttributeError:
                        val = (today, name.string, "", "NT", 0)
                        cursor.execute(query, val)

    print("Neptune Scrape done")
    conn.commit()

    # df = seleccionamos todos los valores que tengan sku registrado
    query = "SELECT * FROM wordpress.scraper WHERE sku != 'NULL'"
    df = pd.read_sql(query, conn)

    # df1 = seleccionamos todos los valores que hayan sido extraidos hoy
    query = "SELECT * FROM wordpress.scraper WHERE ExtractionDate = '" + str(today) + "'"
    df1 = pd.read_sql(query, conn)

    # Sacamos el producto, tipo y el sku de df para luego encontrar los que queremos
    products = df['Product'].to_list()
    b_type = df['ProductType'].to_list()
    competitor = df['Competitor'].to_list()
    skus = df['sku'].to_list()

    products1 = df1['Product'].to_list()
    b_type1 = df1['ProductType'].to_list()
    scraper_id = df1['scraper_id'].to_list()
    competitor1 = df1['Competitor'].to_list()

    query = "UPDATE `wordpress`.`scraper` SET `sku` = %s WHERE (`scraper_id` = %s)"
    for prod, ty, sku, comp in zip(products, b_type, skus, competitor):
        for prod1, ty1, sc_id, comp1 in zip(products1, b_type1, scraper_id, competitor1):
            if prod == prod1 and ty == ty1 and comp == comp1:
                val = (sku, sc_id)
                cursor.execute(query, val)

    conn.commit()
    conn.close()

    print("Redundancy Checker Done")
    print("--- Scraper took %s minutes to finish ---" % round(float((time.time() - start_time)/60), 1))
