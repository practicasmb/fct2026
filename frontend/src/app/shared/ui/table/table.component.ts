import { ChangeDetectionStrategy, Component, Directive, computed, input } from '@angular/core';


@Component({
  selector: 'ui-table',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { style: 'display: contents' },
  template: `
    <div class="relative w-full overflow-auto rounded-lg border border-border">
      <table [class]="classes()">
        <ng-content />
      </table>
    </div>
  `,
})
export class TableComponent {
  class = input<string>('');
  classes = computed(() =>
    ['w-full caption-bottom text-sm', this.class()].filter(Boolean).join(' '),
  );
}


@Directive({
  selector: '[ui-table-header]',
  standalone: true,
  host: { class: '' },
})
export class TableHeaderDirective {}


@Directive({
  selector: '[ui-table-body]',
  standalone: true,
  host: { class: '[&_tr:last-child_td]:border-0 [&_tr:last-child_th]:border-0' },
})
export class TableBodyDirective {}

@Directive({
  selector: '[ui-table-footer]',
  standalone: true,
  host: { class: 'border-t bg-muted/50 font-medium' },
})
export class TableFooterDirective {}


@Directive({
  selector: '[ui-table-row]',
  standalone: true,
  host: { class: 'transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted' },
})
export class TableRowDirective {}


@Directive({
  selector: '[ui-table-head]',
  standalone: true,
  host: {
   class: 'p-4 align-middle text-start font-medium text-foreground border-b border-border [&:has([role=checkbox])]:pr-0',
  },
})
export class TableHeadDirective {}

@Directive({
  selector: '[ui-table-cell]',
  standalone: true,
  host: {
   class: 'p-4 align-middle text-start text-foreground border-b border-border [&:has([role=checkbox])]:pr-0',
  },
})
export class TableCellDirective {}


@Directive({
  selector: '[ui-table-caption]',
  standalone: true,
  host: { class: 'mt-4 text-sm text-muted-foreground' },
})
export class TableCaptionDirective {}


export {
  TableHeaderDirective  as TableHeaderComponent,
  TableBodyDirective    as TableBodyComponent,
  TableFooterDirective  as TableFooterComponent,
  TableRowDirective     as TableRowComponent,
  TableHeadDirective    as TableHeadComponent,
  TableCellDirective    as TableCellComponent,
  TableCaptionDirective as TableCaptionComponent,
};
