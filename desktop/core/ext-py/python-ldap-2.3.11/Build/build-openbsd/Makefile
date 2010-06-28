# $Id: Makefile,v 1.3 2000/08/20 15:04:23 leonard Exp $

WRKDIST=		${.CURDIR}/../..
VERSION!=		sh ${WRKDIST}/Build/version.sh

PKGNAME=		python-ldap-${VERSION}
RUN_DEPENDS=		python:lang/python
CATEGORIES=		misc
MAINATINER=		leonard@users.sourceforge.net
HOMEPAGE=		http://python-ldap.sourceforge.net/

FAKE=			Yes
CONFIGURE_STYLE=	gnu
SEPARATE_BUILD=		Yes
EXTRACT_ONLY=	

CONFIGURE_ARGS+=	--with-ldap=${LOCALBASE}

do-fetch:;

#-- put package on sourceforge ftp server
export-ftp: ${PKGFILE}
	scp ${PKGFILE} python-ldap.sourceforge.net:/home/groups/ftp/pub/python-ldap/${PKGNAME}-${OPSYS}-${ARCH}${PKG_SUFX}

post-build:
	sed -e 's,^${PREFIX}/,,' <${WRKBUILD}/filelist >${WRKBUILD}/filelist2

SED_PLIST+=	|sed -e '/^%%filelist/r${WRKBUILD}/filelist2' -e '//d'
ALL_TARGET=	build filelist

.include <bsd.port.mk>
