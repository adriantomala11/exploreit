# language: en

Feature: Search trips by date

  @searchTripsByDate
  Scenario: Filter tours that contain the word 'Nintendo' in their developer
      Given a set of tours
     | NOMBRE | DESCRIPCION  | UBICACION | HORA_CHECKIN | HORA_SALIDA | HORA_RETORNO | LUGAR_SALIDA | TOKEN | TIPO | PRECIO  | DURACION | CATEGORIA | ABORDAJE_DIA_ANTERIOR |
     | XYZ    | descripcion1 | Chimborazo| 03:15        | 03:15       | 08:15        | Gasolinera   | asdas | NAC  |  95     | 1        | asd       | True                  |
     | ABC    | descripcion2 | Chimborazo| 03:15        | 03:15       | 08:15        | Gasolinera   | asdas | INT  | 505     | 1        | asd       | True                  |
     | DEF    | descripcion3 | Chimborazo| 03:15        | 03:15       | 08:15        | Gasolinera   | asdas | INT  |  75     | 1        | asd       | True                  |
     | GHI    | descripcion4 | Chimborazo| 03:15        | 03:15       | 08:15        | Gasolinera   | asdas | NAC  | 105     | 1        | asd       | True                  |

      Given the user enters the type: INT
      When the user search tours by type
      Then 2 tours will match
      And the tours are
     | ABC    | descripcion2 | Chimborazo| 03:15        | 03:15       | 08:15        | Gasolinera   | asdas | INT  | 505     | 1        | asd       | True                  |
     | DEF    | descripcion3 | Chimborazo| 03:15        | 03:15       | 08:15        | Gasolinera   | asdas | INT  |  75     | 1        | asd       | True                  |
      And the following message is displayed: A game developed by Nintendo was found.

