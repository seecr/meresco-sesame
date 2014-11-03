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

import org.openrdf.repository.sail.SailRepository;
import java.io.File;
import org.openrdf.sail.nativerdf.NativeStore;

class SesameTriplestoreImpl extends SesameTriplestore {

    public SesameTriplestoreImpl(File directory, String storageName) {
        super(directory);
        NativeStore sail = new NativeStore();
        this.repository = new SailRepository(sail);
        this.repository.setDataDir(directory);
        startup();
    }
}