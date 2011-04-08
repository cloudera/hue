<%namespace name="shared" file="shared_components.mako" />

${shared.header("Hue Shell", True, shells)}

## use double hashes for a mako template comment

## this id in the div below ("index") is stripped by Hue.JFrame
## and passed along as the "view" argument in its onLoad event

## the class 'jframe_padded' will give the contents of your window a standard padding
<div id="index" class="view jframe_padded shell_container">
  % if shell_id:
    <span class="shell_id hidden">${shell_id}</span>
  % else:
    <div>
      <ul>
        % for item in shells:
          <li>
          % if item["exists"]:
            <a class="round Button menu_button">${item["niceName"]}</a><span class="hidden">${item["keyName"]}</span>
          % else:
            <a class="round Button disabled">${item["niceName"]}</a>
          % endif
          </li>
        % endfor
      </ul>
    </div>
  % endif
</div>
${shared.footer()}
