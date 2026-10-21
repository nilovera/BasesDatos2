Class Fixture.Partido Extends %Persistent
{
Property Codigo As %String [ Required ];
Property FechaHora As %TimeStamp [ Required ];
Property EquipoLocalId As %String [ Required ];
Property EquipoVisitanteId As %String [ Required ];
Property Estado As %String [ Required ];
Property ArbitroPrincipal As Fixture.Arbitro;

Relationship Eventos As Fixture.EventoPartido
[ Cardinality = children, Inverse = Partido ];

Index idxCodigo On Codigo [ Unique ];

Method CambiarEstado(nuevoEstado As %String) As %Status
{
    If (nuevoEstado'="Programado") && (nuevoEstado'="EnCurso") && (nuevoEstado'="Finalizado") {
        Quit $System.Status.Error(5001,"Estado de partido invalido")
    }
    If (..Estado="Finalizado") {
        Quit $System.Status.Error(5001,"Un partido finalizado no puede cambiar de estado")
    }
    If (..Estado="Programado") && (nuevoEstado="Finalizado") {
        Quit $System.Status.Error(5001,"El partido debe pasar por EnCurso antes de finalizar")
    }
    Set ..Estado = nuevoEstado
    Quit 1
}

Method AgregarEvento(tipo As %String, minuto As %Integer, detalle As %String = "") As %Status
{
    If (..Estado="Finalizado") {
        Quit $System.Status.Error(5001,"No se pueden agregar eventos a un partido finalizado")
    }
    If (minuto<0) || (minuto>130) {
        Quit $System.Status.Error(5001,"El minuto debe estar entre 0 y 130")
    }
    Set evento = ##class(Fixture.EventoPartido).%New()
    Set evento.Tipo = tipo
    Set evento.Minuto = minuto
    Set evento.Detalle = detalle
    Do ..Eventos.Insert(evento)
    Quit 1
}

Method %OnBeforeSave(insert As %Boolean) As %Status
{
    If (..EquipoLocalId=..EquipoVisitanteId) {
        Quit $System.Status.Error(5001,"El equipo local y el visitante deben ser diferentes")
    }
    Quit 1
}
}
