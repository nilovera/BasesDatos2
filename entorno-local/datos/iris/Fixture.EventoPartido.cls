Class Fixture.EventoPartido Extends %Persistent
{
Property Tipo As %String [ Required ];
Property Minuto As %Integer [ Required ];
Property Detalle As %String;

Relationship Partido As Fixture.Partido
[ Cardinality = parent, Inverse = Eventos ];

Index idxPartido On Partido;
}
