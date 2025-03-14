import $ from 'jquery';
import 'jquery.cookie';
import Cookies from 'js-cookie';

describe('Cookie Migration from jquery-cookie to js-cookie', () => {
    afterEach(() => {
        $.removeCookie('test');
        Cookies.remove('test');
    });

    test('migrating from jqeury-cookie to js-cookie should works in getting and setting a cookie api', () => {
        const value = 'value';

        $.cookie('test', value);
        const jqueryCookieValue = $.cookie('test');

        Cookies.set('test', value);
        const jsCookieValue = Cookies.get('test');

        expect(jqueryCookieValue).toEqual(jsCookieValue);
    });

    test('migrating from jqeury-cookie to js-cookie should works in setting the options api', () => {
        const value = 'value';

        $.cookie('test', value, { path: '/', expires: 10 });
        const jqueryCookieValue = $.cookie('test');

        Cookies.set('test', value, { path: '/', expires: 10 });
        const jsCookieValue = Cookies.get('test');

        expect(jqueryCookieValue).toEqual(jsCookieValue);
    });
});
