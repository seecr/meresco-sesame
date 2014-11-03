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

import java.io.File;
import java.nio.charset.Charset;

import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.MissingOptionException;

import sun.misc.Signal;
import sun.misc.SignalHandler;

public class SesameServer {
    public static void main(String[] args) throws Exception {
        Option option;

        Options options = new Options();

        // Port Number
        option = new Option("p", "port", true, "Port number");
        option.setType(Integer.class);
        option.setRequired(true);
        options.addOption(option);

        // Triplestore name
        option = new Option("n", "name", true, "Name of the triplestore");
        option.setType(String.class);
        option.setRequired(true);
        options.addOption(option);

        // Triplestore location
        option = new Option("d", "stateDir", true, "Directory in which triplestore is located");
        option.setType(String.class);
        option.setRequired(true);
        options.addOption(option);

        PosixParser parser = new PosixParser();
        CommandLine commandLine = null;
        try {
            commandLine = parser.parse(options, args);
        } catch (MissingOptionException e) {
            HelpFormatter helpFormatter = new HelpFormatter();
            helpFormatter.printHelp("start-owlim" , options);
            System.exit(1);
        }

        Integer port = new Integer(commandLine.getOptionValue("p"));
        String storeLocation = commandLine.getOptionValue("d");
        String storeName = commandLine.getOptionValue("n");

        if (Charset.defaultCharset() != Charset.forName("UTF-8")) {
        	System.err.println("file.encoding must be UTF-8.");
            System.exit(1);
        }

        long startTime = System.currentTimeMillis();
        Triplestore tripleStore = new SesameTriplestoreImpl(new File(storeLocation), storeName);
        System.out.println("Starting took " + (System.currentTimeMillis() - startTime) / 1000 + " seconds");
        HttpHandler handler = new HttpHandler(tripleStore);
        HttpServer httpServer = new HttpServer(port, 15);

        registerShutdownHandler(tripleStore, httpServer);

        httpServer.setHandler(handler);
        httpServer.start();
    }

    static void registerShutdownHandler(final Triplestore tripleStore, final HttpServer httpServer) {
        Signal.handle(new Signal("TERM"), new SignalHandler() {
            public void handle(Signal sig) {
                shutdown(httpServer, tripleStore);
            }
        });
        Signal.handle(new Signal("INT"), new SignalHandler() {
            public void handle(Signal sig) {
                shutdown(httpServer, tripleStore);
            }
        });
    }

    static void shutdown(final HttpServer httpServer, final Triplestore tripleStore) {
        System.out.println("Shutting down triplestore. Please wait...");
        try {
            tripleStore.shutdown();
            System.out.println("Shutdown completed.");
            System.out.flush();
        } catch (Exception e) {
            e.printStackTrace();
            System.err.flush();
            System.out.println("Shutdown failed.");
            System.out.flush();
        }
        httpServer.stop();
        System.out.println("Http-server stopped");
        System.exit(0);
    }
}
