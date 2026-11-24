from typing import Optional, Literal
from pydantic import BaseModel, Field


class Expose(BaseModel):
    city: str = Field(
        description="Stadt auf Deutsch, korrekt geschrieben, z. B. 'München' statt 'Munich', 'Frankfurt am Main' statt 'FFM'"
    )
    district: Optional[str] = Field(
        None,
        description="Stadtteil, wie im Text angegeben. Wenn kein Stadtteil genannt ist: null"
    )
    property_type: Literal["Eigentumswohnung", "Pflegeapartment", "Mikroapartment"] = Field(
        description="Art der Immobilie. Pflegeapartment = Apartment in einer Pflegeeinrichtung oder Seniorenresidenz. "
                    "Mikroapartment = kleines, oft möbliertes Apartment für Studierende oder Pendler. Sonst: Eigentumswohnung"
    )
    rooms: Optional[float] = Field(
        None,
        description="Anzahl der Zimmer als Zahl, z. B. 2.5 für '2,5 Zimmer'. Wenn nicht angegeben: null"
    )
    size_m2: Optional[float] = Field(
        None,
        description="Wohnfläche in m² als Zahl, z. B. 38.5. Bei zwei verschiedenen Angaben den Wert aus der Wohnflächenberechnung nehmen"
    )
    price_eur: Optional[int] = Field(
        None,
        description="Kaufpreis in Euro als ganze Zahl. '135 T€' = 135000, '349k' = 349000. Bei 'Preis auf Anfrage': null"
    )
    rent_month_eur: Optional[int] = Field(
        None,
        description="Monatliche KALTmiete in Euro. Wenn die Miete pro Jahr angegeben ist, durch 12 teilen. "
                    "Keine Warmmiete, kein Hausgeld. Wenn die Wohnung leer steht oder keine Miete genannt ist: null"
    )


if __name__ == "__main__":
    print(Expose.model_json_schema())