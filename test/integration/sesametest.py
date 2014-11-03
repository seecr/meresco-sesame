## begin license ##
#
# The Meresco Sesame package is an Sesame Triplestore based on meresco-triplestore
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
#
# This file is part of "Meresco Sesame"
#
# "Meresco Sesame" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Sesame" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Sesame"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from os.path import join
from simplejson import loads
from urllib import urlencode
from urllib2 import urlopen, Request
from time import time
from threading import Thread

from weightless.core import compose

from seecr.test.utils import getRequest, postRequest
from seecr.test.integrationtestcase import IntegrationTestCase

from meresco.triplestore import HttpClient, MalformedQueryException, InvalidRdfXmlException
from seecr.test.io import stderr_replaced


class SesameTest(IntegrationTestCase):
    def testOne(self):
        result = urlopen("http://localhost:%s/query?%s" % (self.sesamePort, urlencode(dict(query='SELECT ?x WHERE {}')))).read()
        self.assertTrue('"vars" : [ "x" ]' in result, result)

    def testAddTripleThatsNotATriple(self):
        sesameClient = HttpClient(host='localhost', port=self.sesamePort, synchronous=True)
        try:
            list(compose(sesameClient.addTriple('uri:subject', 'uri:predicate', '')))
            self.fail("should not get here")
        except ValueError, e:
            self.assertEquals('java.lang.IllegalArgumentException: Not a triple: "uri:subject|uri:predicate|"', str(e))

    def testAddInvalidRdf(self):
        sesameClient = HttpClient(host='localhost', port=self.sesamePort, synchronous=True)
        try:
            list(compose(sesameClient.add('uri:identifier', '<invalidRdf/>')))
            self.fail("should not get here")
        except InvalidRdfXmlException, e:
            self.assertEquals('org.openrdf.rio.RDFParseException: Not a valid (absolute) URI: #invalidRdf [line 1, column 14]', str(e))

    def testAddInvalidIdentifier(self):
        sesameClient = HttpClient(host='localhost', port=self.sesamePort, synchronous=True)
        try:
            list(compose(sesameClient.add('identifier', '<ignore/>')))
            self.fail("should not get here")
        except ValueError, e:
            self.assertEquals('java.lang.IllegalArgumentException: Not a valid (absolute) URI: identifier', str(e))

    def testInvalidSparql(self):
        sesameClient = HttpClient(host='localhost', port=self.sesamePort, synchronous=True)
        try:
            list(compose(sesameClient.executeQuery("""select ?x""")))
            self.fail("should not get here")
        except MalformedQueryException, e:
            self.assertTrue(str(e).startswith('org.openrdf.query.MalformedQueryException: Encountered "<EOF>"'), str(e))

    def testKillTripleStoreSavesState(self):
        postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testKillTripleStoreSavesState</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testKillTripleStoreSavesState"}')
        self.assertEquals(1, len(json['results']['bindings']))

        self.restartSesameServer()

        json = self.query('SELECT ?x WHERE {?x ?y "uri:testKillTripleStoreSavesState"}')
        self.assertEquals(1, len(json['results']['bindings']))

    @stderr_replaced
    def testKillTripleStoreWhileDoingQuery(self):
        def doQueries():
            for i in range(1000):
                self.query('SELECT ?x WHERE { ?x ?y ?z }')
        t = Thread(target=doQueries)
        t.start()
        for i in range(100):
            header, body = postRequest(self.sesamePort, "/addTriple", "uri:subject%s|uri:predicate%s|uri:object%s" % (i, i, i), parse=False)
        self.stopSesameServer()
        t.join()
        self.assertTrue('Shutdown completed.' in open(join(self.integrationTempdir, 'stdouterr-sesame.log')).read())
        self.startSesameServer()

    def testDeleteRecord(self):
        postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDelete</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(1, len(json['results']['bindings']))

        postRequest(self.sesamePort, "/update?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDeleteUpdated</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(0, len(json['results']['bindings']))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDeleteUpdated"}')
        self.assertEquals(1, len(json['results']['bindings']))

        postRequest(self.sesamePort, "/delete?identifier=uri:record", "", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(0, len(json['results']['bindings']))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDeleteUpdated"}')
        self.assertEquals(0, len(json['results']['bindings']))

        postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDelete</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(1, len(json['results']['bindings']))

    def testAddAndRemoveTriple(self):
        json = self.query('SELECT ?obj WHERE { <uri:subject> <uri:predicate> ?obj }')
        self.assertEquals(0, len(json['results']['bindings']))

        header, body = postRequest(self.sesamePort, "/addTriple", "uri:subject|uri:predicate|uri:object", parse=False)
        self.assertTrue("200" in header, header)

        json = self.query('SELECT ?obj WHERE { <uri:subject> <uri:predicate> ?obj }')
        self.assertEquals(1, len(json['results']['bindings']))

        header, body = postRequest(self.sesamePort, "/removeTriple", "uri:subject|uri:predicate|uri:object", parse=False)
        self.assertTrue("200" in header, header)
        json = self.query('SELECT ?obj WHERE { <uri:subject> <uri:predicate> ?obj }')
        self.assertEquals(0, len(json['results']['bindings']))

    def testAddPerformance(self):
        totalTime = 0
        try:
            for i in range(10):
                postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description>
                <rdf:type>uri:testFirst%s</rdf:type>
            </rdf:Description>
        </rdf:RDF>""" % i, parse=False)
            number = 1000
            for i in range(number):
                start = time()
                postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description>
                <rdf:type>uri:testSecond%s</rdf:type>
            </rdf:Description>
        </rdf:RDF>""" % i, parse=False)
                totalTime += time() - start
            self.assertTiming(0.00015, totalTime / number, 0.0075)
        finally:
            postRequest(self.sesamePort, "/delete?identifier=uri:record", "")

    def testAddPerformanceInCaseOfThreads(self):
        number = 25
        threads = []
        responses = []
        try:
            for i in range(number):
                def doAdd(i=i):
                    header, body = postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description>
                <rdf:type>uri:testSecond%s</rdf:type>
            </rdf:Description>
        </rdf:RDF>""" % i, parse=False)
                    responses.append((header, body))
                threads.append(Thread(target=doAdd))

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            for header, body in responses:
                self.assertTrue('200 OK' in header, header + '\r\n\r\n' + body)
        finally:
            postRequest(self.sesamePort, "/delete?identifier=uri:record", "")

    def testAcceptHeaders(self):
        postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:test:acceptHeaders</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)

        request = Request('http://localhost:%s/query?%s' % (self.sesamePort, urlencode({'query': 'SELECT ?x WHERE {?x ?y "uri:test:acceptHeaders"}'})), headers={"Accept" : "application/xml"})
        contents = urlopen(request).read()
        self.assertTrue("""<variable name='x'/>""" in contents, contents)

        headers, body = getRequest(self.sesamePort, "/query", arguments={'query': 'SELECT ?x WHERE {?x ?y "uri:test:acceptHeaders"}'}, additionalHeaders={"Accept" : "image/jpg"}, parse=False)

        self.assertEquals(["HTTP/1.1 406 Not Acceptable", "Content-type: text/plain"], headers.split('\r\n')[:2])
        self.assertTrue("""Supported formats SELECT query:""" in body, body)

    def testMimeTypeArgument(self):
        postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about="uri:test:mimeType">
            <rdf:value>Value</rdf:value>
        </rdf:Description>
    </rdf:RDF>""", parse=False)

        request = Request('http://localhost:%s/query?%s' % (self.sesamePort, urlencode({'query': 'SELECT ?x WHERE {?x ?y "Value"}', 'mimeType': 'application/sparql-results+xml'})))
        contents = urlopen(request).read()
        self.assertEqualsWS("""<?xml version='1.0' encoding='UTF-8'?>
<sparql xmlns='http://www.w3.org/2005/sparql-results#'>
    <head>
        <variable name='x'/>
    </head>
    <results>
        <result>
            <binding name='x'>
                <uri>uri:test:mimeType</uri>
            </binding>
        </result>
    </results>
</sparql>""", contents)

    def testDescribeQuery(self):
        postRequest(self.sesamePort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about="uri:test:describe">
            <rdf:value>DESCRIBE</rdf:value>
        </rdf:Description>
    </rdf:RDF>""", parse=False)

        headers, body = getRequest(self.sesamePort, "/query", arguments={'query': 'DESCRIBE <uri:test:describe>'}, additionalHeaders={"Accept" : "application/rdf+xml"}, parse=False)
        self.assertTrue("Content-type: application/rdf+xml" in headers, headers)
        self.assertXmlEquals("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:sesame="http://www.openrdf.org/schema/sesame#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:fn="http://www.w3.org/2005/xpath-functions#">
<rdf:Description rdf:about="uri:test:describe">
    <rdf:value>DESCRIBE</rdf:value>
</rdf:Description></rdf:RDF>""", body)


    def query(self, query):
        return loads(urlopen('http://localhost:%s/query?%s' % (self.sesamePort,
            urlencode(dict(query=query)))).read())

