# CoinRat

## Zadání diplomky
> Cílem práce je vytvořit nástroj pro automatizované obchodování s kryptoměnami (Bitcoin, Ethereum a další), a to pomocí jejich vzájemného směňování. Do tohoto nástroje bude možné integrovat různé obchodní strategie. Jedna z těchto strategií bude implementována přímo v této práci.
> - Využijte již existující řešení (případně i více) pro provádění transakcí mezi různými kryptoměnami. Například shapeshift.io nebo obdobnou službu.
> - Analyzujte používané strategie pro obchodování a navrhněte vhodný reprezentativní model, a ten ověřte v~praxi.
> - Strategie obchodních modelů budou realizovány formou modulu přímo do nástroje. Mohou ale fungovat také tak, že budou volat API jiné služby/systému.
> - Aplikace bude vizualizovat výslednou bilanci a průběh transakcí ve webovém rozhraní.
> - Analýza a volba vhodných technologií je součástí práce.

## Zadání semestrálky na MI-PYT
> - Jádlro umožňují propojit následující položky
> - Napojení na jednu burzu
>   - Adapter na burzu je modul
> - Startegie beží a děla obchody
>   - Strategie je modul
> - Vyzualizace transakcí na webovém rozhraní (backend API)

# Run
* Backend: `cd backend && gunicorn coinrat:app`
