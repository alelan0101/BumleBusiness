 # **Bumle Business – VPN-logovervågning** 

## **1. Baggrund og opgavebeskrivelse** 

Bumle Business er en virksomhed, der benytter en VPN-forbindelse til at oprette sikker forbindelse til virksomhedens servere. Virksomheden har opdaget mistænkelig aktivitet på nogle af sine servere og har mistanke om, at uvedkommende kan have fået adgang via VPN-forbindelsen. 

For at undersøge hændelserne bedre ønsker Bumle Business en løsning, der kan gemme og præsentere logdata fra virksomhedens servere. Løsningen skal gøre det muligt at få et overblik over logdataene ved hjælp af tabeller og diagrammer, så mistænkelig aktivitet lettere kan identificeres og undersøges. 

I projektet skal I udvikle en løsning, der tager udgangspunkt i virksomhedens behov. Samtidig skal I anvende SCRUM som projektstyringsmetode og dokumentere jeres arbejdsproces. 

## **2. Krav til projektledelse** 

Projektet skal gennemføres ved hjælp af SCRUM. 

Følgende krav skal opfyldes: 

1. User Stories: 

Der skal udarbejdes User Stories, som beskriver funktionalitet ud fra brugerens behov. Hver User Story skal indeholde tilhørende Tasks og acceptkriterier. 

2. Sprint: 

Projektet skal planlægges og gennemføres i ét Sprint. 

3. Task Board: 

Der skal oprettes et Task Board, som bruges løbende til at organisere og følge op på projektets opgaver. Boardet skal afspejle opgavernes status undervejs i projektet. 

## **3. Krav til programmering og funktionalitet** 

Den udviklede løsning i udviklet i python skal understøtte følgende: 

- Indlæsning af logs 

De ”rå” logdata skal indlæses i programmets ”memory” fra filen: _cyber_security_log_sample.txt_ (Som I får udleveret sammen med denne projekttekst). 

- Visning af logs: I første omgang skal logdata skal kunne præsenteres i en overskuelig tabel. 

- Analyse af logs: 

I skal undersøge om der er _sammenhænge_ mellem de enkelte kolonner i logfilen med scatter-plots. Når I har fundet en eller flere sammenhænge, skal disse præsenteres på en overskuelig måde med den bedst mulige diagramtype. 

- Visualisering af logs: 

I skal generelt vise relevante diagrammer, der giver et visuelt overblik over logdataene. 

Kode-struktur og kvalitet: I skal designe en samlet kode-løsning de hvor forskellige opgaver placeres i navngivne moduler. Koden skal kommenteres de steder hvor det er rimeligt og alle variabelnavne skal være velvalgte. Der skal i størst muligt omfang bruges egenudviklede genbrugbare funktioner og I skal lave koden rimelig ”fail-safe” med ”exceptions” hvis der er tid. 

De konkrete funktioner og deres acceptkriterier skal beskrives i projektets User Stories. 

## **4. Afleveringskrav** 

Projektet skal afleveres med følgende: 

### **4.1 GitHub** 

- Et link til projektets GitHub-repository. 

- Repositoryet skal indeholde projektets kildekode og relevante filer. 

### **4.2 README.md** 

Projektet skal indeholde en README.md-fil med følgende afsnit: 

1. Introduktion: 

En kort beskrivelse af projektet, dets formål og den problemstilling, det skal løse. 

2. SCRUM: 

   - En forklaring af SCRUM som arbejdsmetode, herunder: 

      - User Stories – hvad de er, og hvordan de bruges. 

      - Tasks – hvad de er, og hvordan de knyttes til User Stories. 

      - Acceptkriterier – hvad de bruges til, og hvordan de definerer, hvornår en opgave er løst. 

      - Task Board – hvad det bruges til, og hvordan det understøtter overblikket over projektets opgaver. 

      - Sammenhængen mellem de forskellige elementer. 

3. Konklusion: En opsummering af det færdige projekt, de vigtigste resultater og eventuelle forbedringsmuligheder.
