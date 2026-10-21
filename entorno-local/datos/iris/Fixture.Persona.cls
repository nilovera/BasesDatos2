Class Fixture.Persona Extends %Persistent
{
Property Documento As %String [ Required ];
Property Nombre As %String [ Required ];
Property Nacionalidad As %String [ Required ];
Property FechaNacimiento As %Date;
Index idxDocumento On Documento [ Unique ];
}
