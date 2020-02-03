---
title: Start developing Hue on a Mac in a few minutes!
author: admin
type: post
date: 2015-03-23T20:06:30+00:00
url: /start-developing-hue-on-a-mac-in-a-few-minutes/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
categories:
  - Development

---
You might have already all the <a href="https://github.com/cloudera/hue#development-prerequisites" target="_blank" rel="noopener noreferrer">pre-requisites</a> installed but we are going to show how to start from a fresh Yosemite (10.10) or El Capitan (10.11) install and end up with running Hue on your Mac in almost no time!

[<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.11.26-1024x768.png"  />][1]

We are going to be using the official <a href="http://www.cloudera.com/content/cloudera/en/downloads/quickstart_vms.html" target="_blank" rel="noopener noreferrer">Quickstart VM</a> from Cloudera that already packs all the Hadoop ecosystem components your Hue will talk to. If you don’t have the latest already downloaded and running, please visit <a href="http://www.cloudera.com/content/cloudera/en/downloads/quickstart_vms.html" target="_blank" rel="noopener noreferrer">this link</a> and choose the versions that suits you the best.

In the meanwhile, let’s set up your Mac!

**Step 1: Clone the Hue repository**

To clone the Hue Github repository you need git installed on your system. Git (plus a ton of other tools) is included in the Xcode command line tools. To install it open Terminal and type

<pre><code class="bash">xcode-select -install</code></pre>

In the dialog choose "Install". If on Terminal you have the message "xcode-select: error: command line tools are already installed, use "Software Update" to install updates" it means you are almost good to go already.

From Terminal, navigate to a directory where you keep all your project and run

<!--email_off-->

<pre><code class="bash">git clone https://github.com/cloudera/hue.git</code></pre>

<!--/email_off-->

You now have the Hue source code in your Mac.

**Step 2: Install Java**

The build process use Java to run. A quick way to get to the right download URL from Oracle is to run from Terminal

<pre><code class="bash">java -version</code></pre>

and then click on the "More info" button on the dialog that appears. On Oracle's website, accept the license and choose the Mac OS X JDK link. After the DMG has been downloaded, open it and double click on the installation package. Now, if we return to the Terminal and type again

<pre><code class="bash">java -version</code></pre>

we will have the version of the freshly installed JDK. At the time of writing, 1.8.0_40.

**Step 3: Install the pre-requisites**

Hue uses several libraries that are not included in the XCode command line tools so we will need to install that too. To do that we will use <a href="http://brew.sh" target="_blank" rel="noopener noreferrer">Homebrew</a>, the fantastic open source package manager for Mac OS X. Install it from Terminal with

<pre><code class="bash">ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"</code></pre>

You will need to enter your password to continue. Then, as suggested by the installation script, run

<pre><code class="bash">brew doctor</code></pre>

If you already have Homebrew installed, just update it running

<pre><code class="bash">brew update</code></pre>

As a first thing, we need to install Maven 3

<pre><code class="bash">brew install maven</code></pre>

And then Mysql to have the development libraries for it

<pre><code class="bash">brew install mysql</code></pre>

This will install also lib-openssl. Let's go on install GMP

<pre><code class="bash">brew install gmp</code></pre>

**Step 3b (just for El Capitan and Sierra): export ENV variables for openssl**

If you have OS X El Capitan or macOS Sierra, you need an extra mini step to be able to make Hue:

<pre><code class="bash">export LDFLAGS=-L/usr/local/opt/openssl/lib && export CPPFLAGS=-I/usr/local/opt/openssl/include</code></pre>

**Step 4: Compile and configure Hue**

Now that we are all set with the requirements we can compile Hue by running

<pre><code class="bash">make apps</code></pre>

from the Hue folder that was created by the git clone in step 1. After a while, if everything goes as planned, you should see as a last build message something like "N static files copied to ...".

[<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.09.20-1024x768.png"  />][2]

Hue comes with a default [configuration file][3] that points all the service to the local machine. Since we are using a VM for this purposes, we will need to change several conf lines. For your convenience, we have the file readily [available here][4].

Just copy this file over to your hue/desktop/conf folder!

**Step 5: Configure your /etc/hosts**

The last thing we should do is to start the Quickstart VM and get its IP address

[<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-08.56.33-1024x688.png"  />][5]

(you can launch the terminal inside the VM and run 'ifconfig' for that; in my case it's 172.16.156.130). Then, on your Mac, edit the hosts file with

<pre><code class="bash">sudo vi /etc/hosts</code></pre>

and add the line

<pre><code class="bash">172.16.156.130 quickstart.cloudera</code></pre>

with the IP you got from the VM. Save and you are good to go!

**Step 6: Run!**

What you have to do on Terminal from the Hue folder is just

<pre><code class="bash">./build/env/bin/hue runserver</code></pre>

And point your browser to <http://localhost:8000>! Go and write a [new app][6] now! 🙂

[<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-13.35.34-1024x716.png"  />][7]

&nbsp;

As usual feel free to comment on the [hue-user][8] list or [@gethue][9]!

 [1]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.11.26.png
 [2]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.09.20.png
 [3]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [4]: https://cdn.gethue.com/uploads/2015/03/pseudo-distributed.ini
 [5]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-08.56.33.png
 [6]: https://gethue.com/start-developing-hue-on-a-mac-in-a-few-minutes/
 [7]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-13.35.34.png
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://twitter.com/gethue
