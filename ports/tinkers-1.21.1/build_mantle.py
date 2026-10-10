from pathlib import Path
import os,subprocess,urllib.request,urllib.parse
P=Path(__file__).resolve().parent
p=next((P/'upstream').iterdir());j=next((P/'runtime').glob('zulu*/bin/java'));e=os.environ.copy();e['JAVA_HOME']=str(j.parent.parent);e['LD_LIBRARY_PATH']=str(j.parent.parent/'lib')+':'+str(j.parent.parent/'lib/server');e['GRADLE_USER_HOME']=str(P/'gradle-cache')
u=urllib.parse.urlparse(urllib.request.getproxies()['https']);(P/'tmp').mkdir(exist_ok=True);opts=['-Djava.net.preferIPv4Stack=true',f'-Djava.io.tmpdir={P / "tmp"}']
for s in ['http','https']:opts += [f'-D{s}.proxyHost={u.hostname}',f'-D{s}.proxyPort={u.port}']
e['JAVA_OPTS']=' '.join(opts)
opts += [f'-Djavax.net.ssl.trustStore={P / "runtime/build-cacerts"}', '-Djavax.net.ssl.trustStorePassword=changeit']
opts.append('-Dorg.gradle.jvmargs=-Xmx3G '+' '.join(opts))
with (P/'mantle-build.log').open('w') as log:
 r=subprocess.run(['bash',str(P/'runtime/gradle-9.2.1/bin/gradle'),'compileJava','--no-daemon','--console=plain','--info',*opts],cwd=p,env=e,stdout=log,stderr=subprocess.STDOUT)
print('exit',r.returncode);print((P/'mantle-build.log').read_text()[-5000:])
