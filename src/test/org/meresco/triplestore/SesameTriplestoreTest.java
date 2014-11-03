/* begin license *
 *
 * The Meresco Sesame package is an Sesame Triplestore based on meresco-triplestore
 *
 * Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
 * Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
 *
 * This file is part of "Meresco Sesame"
 *
 * "Meresco Sesame" is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * "Meresco Sesame" is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with "Meresco Sesame"; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */

package org.meresco.triplestore;

import java.util.List;
import java.util.zip.GZIPInputStream;
import java.io.File;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileInputStream;
import java.io.PrintStream;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import org.junit.Test;
import org.junit.Ignore;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;

import static org.meresco.triplestore.Utils.createTempDirectory;
import static org.meresco.triplestore.Utils.deleteDirectory;

import org.openrdf.query.resultio.TupleQueryResultFormat;
import org.openrdf.repository.RepositoryResult;
import org.openrdf.model.Statement;
import org.openrdf.model.Namespace;
import org.openrdf.model.impl.URIImpl;
import org.openrdf.model.impl.LiteralImpl;

public class SesameTriplestoreTest {
    SesameTriplestoreImpl ts;
    File tempdir;

    @Before
    public void setUp() throws Exception {
        tempdir = createTempDirectory();
        ts = new SesameTriplestoreImpl(tempdir, "storageName");
    }

    @After
    public void tearDown() throws Exception {
        ts.shutdown();
        deleteDirectory(tempdir);
    }

    static final String rdf = "<?xml version='1.0'?>" +
        "<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'" +
        "             xmlns:exterms='http://www.example.org/terms/'>" +
        "  <rdf:Description rdf:about='http://www.example.org/index.html'>" +
        "      <exterms:creation-date>August 16, 1999</exterms:creation-date>" +
        "      <rdf:value>A.M. Özman Yürekli</rdf:value>" +
        "  </rdf:Description>" +
        "</rdf:RDF>";

    @Test
    public void testGetNamespaces() throws Exception {
        ts.add("uri:id0", rdf);
        List<Namespace> namespacesList = ts.getNamespaces();
        assertEquals(2, namespacesList.size());
        assertEquals("http://www.w3.org/1999/02/22-rdf-syntax-ns#", namespacesList.get(0).getName());
        assertEquals("rdf", namespacesList.get(0).getPrefix());
        assertEquals("http://www.example.org/terms/", namespacesList.get(1).getName());
        assertEquals("exterms", namespacesList.get(1).getPrefix());
    }

    @Test
    public void testAddRemoveTriple() throws Exception {
        long startingPoint = ts.size();
        ts.addTriple("uri:subj|uri:pred|uri:obj");
        assertEquals(startingPoint + 1, ts.size());
        ts.removeTriple("uri:subj|uri:pred|uri:obj");
        assertEquals(startingPoint, ts.size());
    }

    @Test
    public void testDelete() throws Exception {
        ts.add("uri:id0", rdf);
        long startingPoint = ts.size();
        ts.delete("uri:id0");
        assertEquals(startingPoint - 2, ts.size());
    }

    @Test
    public void testSparql() throws Exception {
        String answer = null;

        ts.add("uri:id0", rdf);
        answer = ts.executeTupleQuery("SELECT ?x ?y ?z WHERE {?x ?y ?z}", TupleQueryResultFormat.JSON);
        assertTrue(answer.indexOf("\"z\" : {\n        \"type\" : \"literal\",\n        \"value\" : \"A.M. Özman Yürekli\"") > -1);
        assertTrue(answer.endsWith("\n}"));
    }

    @Test
    public void testSparqlResultInXml() throws Exception {
        String answer = null;

        ts.add("uri:id0", rdf);
        answer = ts.executeTupleQuery("SELECT ?x ?y ?z WHERE {?x ?y ?z}", TupleQueryResultFormat.SPARQL);
        assertTrue(answer.startsWith("<?xml"));
        assertTrue(answer.indexOf("<literal>A.M. Özman Yürekli</literal>") > -1);
        assertTrue(answer.endsWith("</sparql>\n"));
    }

    @Test
    public void testShutdown() throws Exception {
        ts.add("uri:id0", rdf);
        ts.shutdown();
        SesameTriplestoreImpl ts = new SesameTriplestoreImpl(tempdir, "storageName");
        assertEquals(2, ts.size());
        ts.shutdown();
    }

    @Test
    public void testExport() throws Exception {
        ts.shutdown();
        ts = new SesameTriplestoreImpl(tempdir, "storageName");
        ts.startup();
        ts.addTriple("uri:subj|uri:pred|uri:obj");
        ts.export("identifier");
        ts.shutdown();
        File backup = new File(new File(tempdir, "backups"), "backup-identifier.trig.gz");
        assertTrue(backup.isFile());
        BufferedReader reader = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(backup))));
        StringBuilder filedata = new StringBuilder();
        String line = reader.readLine();
        while(line != null){
            filedata.append(line);
            line = reader.readLine();
        }
        assertTrue(filedata.toString(), filedata.toString().contains("<uri:subj> <uri:pred> <uri:obj>"));
    }

    String trig = "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> . \n" +
"@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . \n" +
"@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . \n" +
"\n" +
"<uri:aContext> { \n" +
"        <uri:aSubject> <uri:aPredicate> \"a literal  value\" . \n" +
"}";

    @Test
    public void testImport() throws Exception {
        long startingPoint = ts.size();
        ts.importTrig(trig);
        assertEquals(startingPoint + 1, ts.size());
    }
}
